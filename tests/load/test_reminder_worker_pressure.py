import pytest
from django.utils import timezone

from bookings.models import Booking, BookingReminder
from bookings.services.reminders import BookingReminderDeliveryService, schedule_booking_reminders
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_reminder_worker_processes_bounded_batches_under_pressure(settings):
    settings.EMAIL_PROVIDER = "fake"
    for index in range(100):
        booking = create_booking(
            status=Booking.Status.CONFIRMED,
            starts_at=timezone.now() + timezone.timedelta(days=1, minutes=index),
            idempotency_key=f"reminder-pressure-{index}",
        )
        schedule_booking_reminders(booking)
    BookingReminder.objects.update(scheduled_for=timezone.now() - timezone.timedelta(minutes=1))

    first = BookingReminderDeliveryService.send_due(limit=40)
    second = BookingReminderDeliveryService.send_due(limit=200)

    assert first.sent == 40
    assert first.sent + second.sent == 100
    assert BookingReminder.objects.filter(status=BookingReminder.Status.SENT).count() == 100
