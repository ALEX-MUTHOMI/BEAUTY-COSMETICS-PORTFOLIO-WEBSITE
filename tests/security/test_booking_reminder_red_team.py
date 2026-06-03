import pytest
from django.utils import timezone

from bookings.models import BookingReminder
from bookings.services.reminders import BookingReminderDeliveryService, schedule_booking_reminders
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_reminder_red_team_skips_cancelled_erased_and_redacts_content(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(days=1))
    schedule_booking_reminders(booking)
    booking.customer_profile.erase()
    BookingReminder.objects.filter(booking=booking).update(scheduled_for=timezone.now() - timezone.timedelta(minutes=1))

    result = BookingReminderDeliveryService.send_due(limit=10)
    reminder = BookingReminder.objects.get(booking=booking, reminder_type=BookingReminder.ReminderType.APPOINTMENT_24H)

    assert result.skipped == 1
    assert reminder.status == BookingReminder.Status.SKIPPED
    assert "grace@example.com" not in reminder.failure_reason_redacted
    assert "+254" not in reminder.failure_reason_redacted
