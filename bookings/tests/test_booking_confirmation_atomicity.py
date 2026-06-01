from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingAuditEvent, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _checkout_and_success_ledger(booking, checkout_key="atomic-checkout"):
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=checkout_key,
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference=f"provider-{checkout_key}",
        provider_receipt=f"receipt-{checkout_key}",
    )
    return session, ledger


@pytest.mark.django_db(transaction=True)
def test_confirmation_rolls_back_if_operational_history_creation_fails(monkeypatch):
    booking = _held_booking(key="atomic-rollback")
    session, ledger = _checkout_and_success_ledger(booking)

    from bookings.services import checkout_contract

    original_create_history = checkout_contract._create_history

    def fail_on_success_history(*args, **kwargs):
        if args[1] == "payment_success":
            raise RuntimeError("simulated history outage")
        return original_create_history(*args, **kwargs)

    monkeypatch.setattr(checkout_contract, "_create_history", fail_on_success_history)

    with pytest.raises(RuntimeError):
        _contract_service().confirm_booking_after_billing_success(
            checkout_session=session,
            billing_ledger=ledger,
            request_context={"request_id": "atomic-redacted"},
        )

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert booking.confirmed_at is None
    assert BookingAuditEvent.objects.filter(booking=booking, new_status=Booking.Status.CONFIRMED).count() == 0
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_success").count() == 0


@pytest.mark.django_db(transaction=True)
def test_confirmation_rejects_missing_success_ledger_without_partial_state():
    booking = _held_booking(key="atomic-missing-ledger")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="atomic-missing-ledger-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])

    class FakeLedger:
        id = "fake-ledger"
        amount = Decimal("2500.00")
        currency = "KES"
        status = "success"
        external_correlation_id = str(session.id)

    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=FakeLedger())

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 0
