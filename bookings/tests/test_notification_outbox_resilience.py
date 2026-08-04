import pytest
from django.utils import timezone

from bookings.models import BookingNotification
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_outbox_batch_limit_and_one_bad_notification_does_not_block_batch(settings):
    settings.EMAIL_PROVIDER = "fake"
    good_one, _session, _ledger = _confirm_paid_booking("outbox-good-one")
    bad, _session, _ledger = _confirm_paid_booking("outbox-bad")
    good_two, _session, _ledger = _confirm_paid_booking("outbox-good-two")
    bad.status = "held"
    bad.save(update_fields=["status", "updated_at"])

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    result = BookingNotificationDeliveryService.send_pending(limit=2)
    assert result.sent == 1
    assert result.skipped == 1
    assert BookingNotification.objects.filter(booking=good_one, status=BookingNotification.Status.SENT).count() == 1
    assert BookingNotification.objects.filter(booking=good_two, status=BookingNotification.Status.PENDING).count() == 1


@pytest.mark.django_db(transaction=True)
def test_provider_failure_caps_attempts_and_marks_final(monkeypatch, settings):
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_NOTIFICATION_MAX_ATTEMPTS = 2
    booking, _session, _ledger = _confirm_paid_booking("outbox-final")

    from bookings.services import notification_delivery
    from bookings.services.email_provider import EmailProviderError

    class FailingProvider:
        def send_email(self, **kwargs):
            raise EmailProviderError("provider 429 quota exceeded for victim@example.com")

    monkeypatch.setattr(notification_delivery, "get_email_provider", lambda: FailingProvider())

    first = notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10)
    assert first.failed == 1
    notification = BookingNotification.objects.get(booking=booking)
    assert notification.status == BookingNotification.Status.RETRY_SCHEDULED
    assert notification.scheduled_for > timezone.now()
    assert "victim@example.com" not in notification.last_error_redacted

    notification.scheduled_for = timezone.now()
    notification.save(update_fields=["scheduled_for", "updated_at"])
    second = notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10)
    notification.refresh_from_db()
    assert second.failed == 1
    assert notification.status == BookingNotification.Status.FAILED_FINAL
