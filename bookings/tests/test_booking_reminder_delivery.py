import pytest
from django.utils import timezone

from bookings.models import Booking, BookingReminder
from bookings.services.reminders import BookingReminderDeliveryService, schedule_booking_reminders
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_due_reminder_delivery_uses_fake_provider_and_failures_do_not_corrupt_booking(settings, monkeypatch):
    from bookings.services import reminders
    from bookings.services.email_provider import EmailProviderError

    settings.EMAIL_PROVIDER = "fake"
    booking = create_booking(status=Booking.Status.CONFIRMED, starts_at=timezone.now() + timezone.timedelta(days=1))
    schedule_booking_reminders(booking)
    BookingReminder.objects.filter(booking=booking).update(scheduled_for=timezone.now() - timezone.timedelta(minutes=1))

    result = BookingReminderDeliveryService.send_due(limit=10)
    reminder = BookingReminder.objects.get(booking=booking, reminder_type=BookingReminder.ReminderType.APPOINTMENT_24H)
    assert result.sent == 1
    assert reminder.status == BookingReminder.Status.SENT

    second = create_booking(status=Booking.Status.CONFIRMED, starts_at=timezone.now() + timezone.timedelta(days=1))
    schedule_booking_reminders(second)
    BookingReminder.objects.filter(booking=second).update(scheduled_for=timezone.now() - timezone.timedelta(minutes=1))

    class FailingProvider:
        provider = "fake"

        def send_email(self, **_kwargs):
            raise EmailProviderError("429 provider quota for grace@example.com +254712345678")

    monkeypatch.setattr(reminders, "get_email_provider", lambda: FailingProvider())
    failed = BookingReminderDeliveryService.send_due(limit=10)
    second.refresh_from_db()
    failed_reminder = BookingReminder.objects.get(
        booking=second, reminder_type=BookingReminder.ReminderType.APPOINTMENT_24H
    )
    assert failed.failed == 1
    assert second.status == Booking.Status.CONFIRMED
    assert failed_reminder.status in {BookingReminder.Status.PENDING, BookingReminder.Status.FAILED}
    assert "grace@example.com" not in failed_reminder.failure_reason_redacted
