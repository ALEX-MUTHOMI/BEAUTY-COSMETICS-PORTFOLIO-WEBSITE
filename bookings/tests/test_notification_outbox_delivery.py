import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingNotification
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirmed_booking(key):
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
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    return booking


@pytest.mark.django_db(transaction=True)
def test_fake_provider_sends_pending_notifications_once(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = _confirmed_booking("notify-send")

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    assert result.sent == 2
    assert BookingNotification.objects.filter(booking=booking, status=BookingNotification.Status.SENT).count() == 2
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 0


@pytest.mark.django_db(transaction=True)
def test_provider_failure_records_redacted_error_and_retry_can_succeed(settings, monkeypatch):
    settings.EMAIL_PROVIDER = "fake"
    booking = _confirmed_booking("notify-failure")

    from bookings.services import notification_delivery
    from bookings.services.email_provider import EmailProviderError

    class FailingProvider:
        def send_email(self, **_kwargs):
            raise EmailProviderError("provider failed with secret-token and user@example.com")

    monkeypatch.setattr(notification_delivery, "get_email_provider", lambda: FailingProvider())
    result = notification_delivery.BookingNotificationDeliveryService.send_pending(limit=1)
    assert result.failed == 1
    failed = BookingNotification.objects.filter(booking=booking, status=BookingNotification.Status.FAILED).first()
    assert failed.attempts == 1
    assert "secret-token" not in failed.last_error_redacted
    assert "user@example.com" not in failed.last_error_redacted

    failed.status = BookingNotification.Status.PENDING
    failed.save(update_fields=["status", "updated_at"])
    monkeypatch.undo()
    assert notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10).sent >= 1


@pytest.mark.django_db(transaction=True)
def test_erased_or_unconfirmed_customer_notifications_are_skipped(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = _confirmed_booking("notify-skip")
    booking.customer_profile.erase()
    BookingNotification.objects.filter(booking=booking).update(status=BookingNotification.Status.PENDING)

    pending = _held_booking(key="notify-unconfirmed")
    pending_notification = BookingNotification.objects.create(
        booking=pending,
        notification_type="booking_confirmed",
        channel=BookingNotification.Channel.EMAIL,
        recipient_email_hash="hash",
        recipient_email_redacted="g***@example.com",
    )

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    pending_notification.refresh_from_db()
    assert result.skipped >= 2
    assert pending_notification.status == BookingNotification.Status.CANCELLED
    assert Booking.objects.get(pk=pending.pk).status == Booking.Status.HELD
