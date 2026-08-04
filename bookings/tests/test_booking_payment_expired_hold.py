from datetime import timedelta

import pytest
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_late_success_after_expired_hold_does_not_confirm_and_routes_to_manual_review():
    booking = _held_booking(key="late-expired-hold")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="late-expired-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    booking.status = Booking.Status.EXPIRED
    booking.hold_expires_at = timezone.now() - timedelta(minutes=1)
    booking.save(update_fields=["status", "hold_expires_at", "updated_at"])

    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="late-provider-reference",
        provider_receipt="late-provider-receipt",
        raw_payload={"safe": "redacted"},
        correlation_id="late-expired",
    )
    _contract_service().reconcile_late_payment_for_expired_hold(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert booking.status == Booking.Status.EXPIRED
    assert (
        BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_received_after_expiry").count() == 1
    )
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="requires_manual_review").count() == 1


@pytest.mark.django_db(transaction=True)
def test_late_success_reconciliation_is_idempotent():
    booking = _held_booking(key="late-expired-idem")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="late-expired-idem-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    booking.status = Booking.Status.EXPIRED
    booking.save(update_fields=["status", "updated_at"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="late-provider-reference-2",
        provider_receipt="late-provider-receipt-2",
    )

    _contract_service().reconcile_late_payment_for_expired_hold(checkout_session=session, billing_ledger=ledger)
    _contract_service().reconcile_late_payment_for_expired_hold(checkout_session=session, billing_ledger=ledger)

    assert (
        BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_received_after_expiry").count() == 1
    )
