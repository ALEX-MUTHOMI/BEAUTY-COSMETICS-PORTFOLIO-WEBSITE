import pytest
from django.utils import timezone

from bookings.models import Booking, BookingReminder
from bookings.services.reminders import schedule_booking_reminders
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_confirmed_booking_schedules_utc_idempotent_reminders_only_for_valid_states():
    booking = create_booking(status=Booking.Status.CONFIRMED, starts_at=timezone.now() + timezone.timedelta(days=3))

    created = schedule_booking_reminders(booking)
    replay = schedule_booking_reminders(booking)

    assert len(created) >= 1
    assert replay == []
    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.PENDING).count() == len(
        created
    )
    assert all(reminder.scheduled_for.tzinfo for reminder in created)

    failed = create_booking(status=Booking.Status.PAYMENT_FAILED)
    assert schedule_booking_reminders(failed) == []
