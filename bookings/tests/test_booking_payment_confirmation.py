from decimal import Decimal

import pytest
from django.utils import timezone

from billing.models import LedgerTransaction
from bookings.models import Booking, BookingAuditEvent, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.exceptions import CheckoutValidationError
from checkout.models import CheckoutSession
from checkout.services import initiate_mpesa_stk, process_mpesa_callback


@pytest.mark.django_db(transaction=True)
def test_stk_sent_does_not_confirm_but_successful_billing_ledger_confirms_once():
    booking = _held_booking(key="confirm-success")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="confirm-success-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])

    attempt = initiate_mpesa_stk(session.id, "+254712345678", "confirm-success-stk")
    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 0

    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "2500.00",
        "MpesaReceiptNumber": "QBOOKING001",
    }
    process_mpesa_callback(payload, remote_addr="127.0.0.1", correlation_id="booking-success")
    process_mpesa_callback(payload, remote_addr="127.0.0.1", correlation_id="booking-success")

    booking.refresh_from_db()
    ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))
    assert booking.status == Booking.Status.CONFIRMED
    assert booking.confirmed_at is not None
    assert timezone.is_aware(booking.confirmed_at)
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert booking.checkout_session_id == str(session.id)
    assert BookingAuditEvent.objects.filter(booking=booking, new_status=Booking.Status.CONFIRMED).count() == 1
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_success").count() == 1
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 1


@pytest.mark.django_db(transaction=True)
def test_amount_mismatch_does_not_confirm_booking():
    booking = _held_booking(key="confirm-mismatch")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="confirm-mismatch-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "confirm-mismatch-stk")

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "9999.00",
                "MpesaReceiptNumber": "QMISMATCHBOOKING",
            },
            remote_addr="127.0.0.1",
        )

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert (
        LedgerTransaction.objects.filter(external_correlation_id=str(session.id), amount=Decimal("9999.00")).count()
        == 0
    )
