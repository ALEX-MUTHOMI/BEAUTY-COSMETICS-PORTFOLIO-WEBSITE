import logging
from datetime import timedelta

import pytest
from django.utils import timezone

from bookings.models import Booking, BookingReminder
from bookings.services.reminders import cancel_pending_reminders, create_pending_reminder, reminder_is_sendable
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_confirmed_booking_can_create_pending_reminder():
    booking = create_booking(status=Booking.Status.CONFIRMED)

    reminder = create_pending_reminder(
        booking,
        channel=BookingReminder.Channel.SMS,
        scheduled_for=timezone.now() + timedelta(hours=1),
    )

    assert reminder.status == BookingReminder.Status.PENDING
    assert reminder_is_sendable(reminder) is True


@pytest.mark.django_db
def test_cancelling_booking_cancels_pending_reminders():
    booking = create_booking(status=Booking.Status.CONFIRMED)
    reminder = create_pending_reminder(
        booking,
        channel=BookingReminder.Channel.EMAIL,
        scheduled_for=timezone.now() + timedelta(hours=1),
    )

    cancel_pending_reminders(booking)

    reminder.refresh_from_db()
    assert reminder.status == BookingReminder.Status.CANCELLED


@pytest.mark.django_db
def test_erased_customer_blocks_reminder_send_and_logs_are_redacted(caplog):
    booking = create_booking(status=Booking.Status.CONFIRMED)
    booking.customer_profile.erase()
    reminder = create_pending_reminder(
        booking,
        channel=BookingReminder.Channel.SMS,
        scheduled_for=timezone.now() + timedelta(hours=1),
    )

    with caplog.at_level(logging.INFO):
        assert reminder_is_sendable(reminder) is False

    assert booking.customer_profile.phone_redacted not in caplog.text
