import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _session_and_ledger(key):
    booking = _held_booking(key=key)
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"{key}-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference=f"provider-{key}",
        provider_receipt=f"receipt-{key}",
    )
    return booking, session, ledger


@pytest.mark.django_db(transaction=True)
def test_failure_after_success_does_not_deconfirm_booking():
    booking, session, ledger = _session_and_ledger("failure-after-success")
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    _contract_service().fail_booking_after_payment_failure(
        checkout_session=session,
        failure_reason="late_provider_timeout",
        request_context={"request_id": "failure-after-success"},
    )

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_failed").count() == 0


@pytest.mark.django_db(transaction=True)
def test_success_after_failure_uses_manual_review_policy_not_accidental_confirmation():
    booking, session, ledger = _session_and_ledger("success-after-failure")
    _contract_service().fail_booking_after_payment_failure(
        checkout_session=session,
        failure_reason="provider_failed",
        request_context={"request_id": "success-after-failure"},
    )

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_FAILED
    assert (
        BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_received_after_failure").count()
        == 1
    )
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="requires_manual_review").count() == 1
