from bookings.models import BookingReminder


def create_pending_reminder(booking, channel, scheduled_for):
    return BookingReminder.objects.create(
        booking=booking,
        channel=channel,
        scheduled_for=scheduled_for,
    )


def cancel_pending_reminders(booking):
    return booking.reminders.filter(status=BookingReminder.Status.PENDING).update(
        status=BookingReminder.Status.CANCELLED
    )


def reminder_is_sendable(reminder):
    if reminder.booking.customer_profile.erased_at:
        return False
    return reminder.status == BookingReminder.Status.PENDING and reminder.booking.customer_profile.reminder_consent
