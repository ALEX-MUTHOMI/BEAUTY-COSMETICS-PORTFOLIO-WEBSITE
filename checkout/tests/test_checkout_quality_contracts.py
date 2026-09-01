"""Quality contracts for checkout expiry capacity + FAILED webhook retry."""

import pytest

from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.services import expire_checkout_session, record_mpesa_webhook_event


@pytest.mark.django_db(transaction=True)
def test_expire_checkout_fails_payment_pending_booking_and_frees_capacity(monkeypatch):
    booking = _held_booking(key="checkout-expire-capacity")
    checkout_result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="checkout-expire-capacity-key",
    )
    session = CheckoutSession.objects.get(id=checkout_result["checkout_public_id"])
    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING

    bumps = []

    def capture(**kwargs):
        bumps.append((kwargs["old_status"], kwargs["new_status"], kwargs["local_date"]))

    monkeypatch.setattr(
        "bookings.services.state_machine.invalidate_calendar_capacity_for_transition",
        capture,
    )

    expire_checkout_session(session.id)
    session.refresh_from_db()
    booking.refresh_from_db()
    assert session.status == CheckoutSession.Status.EXPIRED
    assert booking.status == Booking.Status.PAYMENT_FAILED
    assert any(old == Booking.Status.PAYMENT_PENDING and new == Booking.Status.PAYMENT_FAILED for old, new, _ in bumps)


@pytest.mark.django_db(transaction=True)
def test_failed_webhook_inbox_allows_retry_not_duplicate():
    payload = {
        "CheckoutRequestID": "ws_CO_FAILED_RETRY",
        "ResultCode": 0,
        "Amount": "100.00",
    }
    first = record_mpesa_webhook_event(payload, correlation_id="failed-retry")
    MpesaWebhookInbox.objects.filter(pk=first.pk).update(processing_status=MpesaWebhookInbox.Status.FAILED)
    first.refresh_from_db()
    assert first.processing_status == MpesaWebhookInbox.Status.FAILED

    retry = record_mpesa_webhook_event(payload, correlation_id="failed-retry-2")
    assert retry.pk == first.pk
    assert retry.processing_status == MpesaWebhookInbox.Status.FAILED
    assert MpesaWebhookInbox.objects.filter(event_hash=first.event_hash).count() == 1
