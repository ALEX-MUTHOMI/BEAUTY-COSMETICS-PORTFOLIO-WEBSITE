import pytest
from django.test import Client

from bookings.models import BookingNotification
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_quota_hard_limit_keeps_booking_confirmed_and_status_customer_safe(settings, tmp_path):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    settings.EMAIL_DAILY_HARD_LIMIT = 0
    booking, _session, _ledger = _confirm_paid_booking("quota-status-safe")

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification = BookingNotification.objects.get(booking=booking)
    payload = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True).json()

    assert result.sent == 0
    assert result.failed == 1
    assert notification.status == BookingNotification.Status.QUOTA_BLOCKED
    assert notification.failure_code == "email_quota_hard_limit"
    assert booking.notifications.count() == 1
    assert booking.receipt.pdf_artifact.status == "ready"
    assert payload["booking_status"] == "confirmed"
    assert payload["payment_status"] == "paid"
    assert payload["email_status"] == "receipt_email_delayed"
    assert "quota" not in str(payload).lower()
