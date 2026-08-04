import pytest

from billing.models import LedgerTransaction
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession
from checkout.services import initiate_mpesa_stk, process_mpesa_callback


@pytest.mark.django_db(transaction=True)
def test_checkout_billing_booking_hardening_contract_confirms_and_creates_receipt_once():
    booking = _held_booking(key="b4a-integration-success")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="b4a-integration-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "b4a-integration-stk")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "2500.00",
        "MpesaReceiptNumber": "QB4AHARDENED",
    }

    process_mpesa_callback(payload, remote_addr="127.0.0.1", correlation_id="b4a-hardening")
    process_mpesa_callback(payload, remote_addr="127.0.0.1", correlation_id="b4a-hardening")

    from bookings.models import BookingNotification, BookingReceipt

    booking.refresh_from_db()
    ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))
    assert booking.status == Booking.Status.CONFIRMED
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 1
    assert BookingReceipt.objects.filter(booking=booking, billing_ledger_id=str(ledger.id)).count() == 1
    assert (
        BookingNotification.objects.filter(
            booking=booking,
            notification_type="booking_confirmed_with_receipt",
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_failed_callback_does_not_create_receipt_or_success_ledger():
    booking = _held_booking(key="b4a-integration-failure")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="b4a-integration-failure-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "b4a-integration-failure-stk")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 1032,
            "Amount": "2500.00",
        },
        remote_addr="127.0.0.1",
    )

    from bookings.models import BookingReceipt

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_FAILED
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id), status="success").count() == 0
    assert BookingReceipt.objects.filter(booking=booking).count() == 0
