import pytest
from django.test import Client
from django.utils import timezone

from bookings.models import BookingReminder
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_status_portal_exposes_reminder_and_reschedule_contract_without_otp(settings, tmp_path):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService
    from bookings.services.reminders import schedule_booking_reminders

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("status-portal-b5")
    booking.starts_at = timezone.now() + timezone.timedelta(days=5)
    booking.ends_at = booking.starts_at + timezone.timedelta(minutes=booking.service.duration_minutes)
    booking.save(update_fields=["starts_at", "ends_at", "updated_at"])
    schedule_booking_reminders(booking)
    BookingNotificationDeliveryService.send_pending(limit=10)

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["booking_status"] == "confirmed"
    assert payload["payment_status"] == "paid"
    assert payload["reminder_status"] == "scheduled"
    assert payload["reschedule"]["eligible"] is True
    assert payload["reschedule"]["requires_otp"] is True
    assert "deadline_eat" in payload["reschedule"]
    assert BookingReminder.objects.filter(booking=booking, status=BookingReminder.Status.PENDING).exists()


@pytest.mark.django_db(transaction=True)
def test_status_portal_pending_payment_and_delayed_email_are_safe(settings, tmp_path):
    from bookings.models import Booking, BookingNotification
    from bookings.tests.factories import create_booking

    booking = create_booking(status=Booking.Status.PAYMENT_PENDING)
    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["payment_status"] == "payment_pending"
    assert payload["email_status"] == "receipt_email_queued"
    assert payload["reminder_status"] == "not_scheduled"
    assert "quota" not in str(payload).lower()
    assert "provider" not in str(payload).lower()
    assert BookingNotification.objects.filter(booking=booking).count() == 0
