from datetime import timedelta

import pytest
from django.utils import timezone

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingAuditEvent, BookingFinancialHistory
from bookings.tests.factories import create_booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _expired_booking_payment(key):
    booking = _held_booking(key=key)
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"{key}-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    booking.status = Booking.Status.EXPIRED
    booking.hold_expires_at = timezone.now() - timedelta(minutes=1)
    booking.save(update_fields=["status", "hold_expires_at", "updated_at"])
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
def test_late_payment_after_expired_hold_never_auto_confirms_and_is_deduped():
    booking, session, ledger = _expired_booking_payment("late-payment-b4a")

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.EXPIRED
    assert (
        BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_received_after_expiry").count() == 1
    )
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="requires_manual_review").count() == 1
    assert BookingAuditEvent.objects.filter(booking=booking, reason="payment_received_after_expiry").count() == 1


@pytest.mark.django_db(transaction=True)
def test_late_payment_after_slot_taken_does_not_double_book():
    booking, session, ledger = _expired_booking_payment("late-slot-taken")
    occupying = create_booking(
        customer_profile=booking.customer_profile,
        service=booking.service,
        resource=booking.resource,
        starts_at=booking.starts_at,
        ends_at=booking.ends_at,
        status=Booking.Status.CONFIRMED,
        confirmed_at=timezone.now(),
        idempotency_key="late-slot-taken-occupying",
    )

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    occupying.refresh_from_db()
    assert booking.status == Booking.Status.EXPIRED
    assert occupying.status == Booking.Status.CONFIRMED
    assert (
        Booking.objects.filter(
            resource=booking.resource, starts_at=booking.starts_at, status=Booking.Status.CONFIRMED
        ).count()
        == 1
    )
