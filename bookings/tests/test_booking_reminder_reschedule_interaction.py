import pytest
from django.utils import timezone

from bookings.models import Booking, BookingReminder
from bookings.services.reminders import schedule_booking_reminders
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_successful_reschedule_cancels_old_reminders_and_creates_new_reminders():
    from bookings.models import CustomerOTPChallenge
    from bookings.services.customer_otp import CustomerOTPService
    from bookings.services.rescheduling import BookingRescheduleService

    booking = create_booking(status=Booking.Status.CONFIRMED, starts_at=timezone.now() + timezone.timedelta(days=5))
    schedule_booking_reminders(booking)
    old_count = BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.PENDING).count()
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.20", "user_agent": "pytest"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)

    new_start = booking.starts_at + timezone.timedelta(days=2)
    BookingRescheduleService.reschedule(
        booking_public_id=booking.public_id,
        action_token=action.token,
        requested_starts_at=new_start,
    )

    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.CANCELLED).count() == old_count
    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.PENDING).exists()
