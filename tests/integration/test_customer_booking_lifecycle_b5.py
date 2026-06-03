import pytest
from django.test import Client
from django.utils import timezone

from bookings.models import BookingReminder, CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.reminders import BookingReminderDeliveryService, schedule_booking_reminders
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_guest_confirmed_booking_status_reminder_otp_reschedule_lifecycle(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("customer-lifecycle-b5")
    booking.starts_at = timezone.now() + timezone.timedelta(days=5)
    booking.ends_at = booking.starts_at + timezone.timedelta(minutes=booking.service.duration_minutes)
    booking.save(update_fields=["starts_at", "ends_at", "updated_at"])

    schedule_booking_reminders(booking)
    BookingReminder.objects.filter(booking=booking).update(scheduled_for=timezone.now() - timezone.timedelta(minutes=1))
    delivery = BookingReminderDeliveryService.send_due(limit=10)
    assert delivery.sent >= 1

    status = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    assert status.status_code == 200
    assert status.json()["reschedule"]["requires_otp"] is True

    challenge = CustomerOTPService.request_challenge(
        booking_public_id=booking.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.40", "user_agent": "pytest"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)
    new_start = (booking.starts_at + timezone.timedelta(days=2)).replace(second=0, microsecond=0)
    updated = BookingRescheduleService.reschedule(
        booking_public_id=booking.public_id,
        action_token=action.token,
        requested_starts_at=new_start,
    )

    assert updated.starts_at == new_start
    assert updated.status == "confirmed"
    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.SENT).exists()
    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.PENDING).exists()
