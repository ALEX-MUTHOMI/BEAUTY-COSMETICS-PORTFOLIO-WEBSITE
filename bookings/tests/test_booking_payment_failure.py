import pytest

from billing.models import LedgerTransaction
from bookings.models import Booking, BookingAuditEvent, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession
from checkout.services import initiate_mpesa_stk, process_mpesa_callback


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("result_code", [1, 1032, 1037])
def test_failed_cancelled_and_timeout_callbacks_do_not_confirm_booking(result_code):
    booking = _held_booking(key=f"failed-payment-{result_code}")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"failed-payment-checkout-{result_code}",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", f"failed-payment-stk-{result_code}")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": result_code,
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
    assert BookingAuditEvent.objects.filter(booking=booking, new_status=Booking.Status.PAYMENT_FAILED).exists()
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_failed").exists()


@pytest.mark.django_db(transaction=True)
def test_failure_after_success_does_not_deconfirm_booking():
    booking = _held_booking(key="failure-after-success")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="failure-after-success-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    attempt = initiate_mpesa_stk(session.id, "+254712345678", "failure-after-success-stk")
    success = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "2500.00",
        "MpesaReceiptNumber": "QBOOKING002",
    }
    process_mpesa_callback(success, remote_addr="127.0.0.1")
    process_mpesa_callback({**success, "ResultCode": 1032}, remote_addr="127.0.0.1")

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_success").count() == 1
