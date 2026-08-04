import pytest

from billing.models import LedgerTransaction
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession
from checkout.services import initiate_mpesa_stk, process_mpesa_callback


@pytest.mark.django_db(transaction=True)
def test_booking_checkout_billing_success_contract_confirms_booking_once():
    booking = _held_booking(key="integration-b4-success")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="integration-b4-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "integration-b4-stk")

    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "2500.00",
        "MpesaReceiptNumber": "QB4SUCCESS",
    }
    process_mpesa_callback(payload, remote_addr="127.0.0.1")
    process_mpesa_callback(payload, remote_addr="127.0.0.1")

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id), status=LedgerTransaction.Status.SUCCESS
        ).count()
        == 1
    )
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 1


@pytest.mark.django_db(transaction=True)
def test_booking_checkout_billing_failure_contract_does_not_credit_or_confirm():
    booking = _held_booking(key="integration-b4-failure")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="integration-b4-failure-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "integration-b4-failure-stk")
    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 1032,
            "Amount": "2500.00",
        },
        remote_addr="127.0.0.1",
    )

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_FAILED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id), status=LedgerTransaction.Status.SUCCESS
        ).count()
        == 0
    )
