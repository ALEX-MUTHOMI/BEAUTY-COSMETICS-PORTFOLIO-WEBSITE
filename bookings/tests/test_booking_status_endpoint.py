import pytest
from django.test import Client

from bookings.models import Booking, BookingNotification, FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_tuesday, make_customer_payload, make_resource
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_confirmed_booking_status_endpoint_is_small_safe_and_customer_friendly(settings, tmp_path):
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("status-confirmed")
    BookingNotificationDeliveryService.send_pending(limit=10)

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["booking_reference"] == str(booking.public_id)
    assert payload["booking_status"] == "confirmed"
    assert payload["payment_status"] == "paid"
    assert payload["receipt_status"] == "pdf_generated"
    assert payload["email_status"] == "receipt_email_sent"
    assert payload["next_action"] == "none"
    assert "service" in payload
    assert "schedule" in payload
    assert str(booking.id) not in str(payload)
    assert "grace@example.com" not in str(payload)
    assert "+254" not in str(payload)
    assert "provider-" not in str(payload)
    assert "receipt-" not in str(payload).lower()


@pytest.mark.django_db(transaction=True)
def test_pending_and_quota_blocked_statuses_are_customer_safe(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("status-delayed")
    notification = BookingNotification.objects.get(booking=booking)
    notification.status = BookingNotification.Status.QUOTA_BLOCKED
    notification.last_error_redacted = "provider quota 429"
    notification.save(update_fields=["status", "last_error_redacted", "updated_at"])

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["booking_status"] == "confirmed"
    assert payload["payment_status"] == "paid"
    assert payload["email_status"] == "receipt_email_delayed"
    assert "quota" not in str(payload).lower()
    assert "429" not in str(payload)


@pytest.mark.django_db(transaction=True)
def test_full_package_booking_status_endpoint_is_safe_without_single_service():
    resource = make_resource()
    package = FullPackage.objects.create(
        name="<b>Complete Bridal Package</b>",
        slug="complete-bridal-status",
        duration_minutes=300,
        price_amount="15000.00",
    )
    result = BookingHoldService.create_full_package_hold(
        full_package_public_id=str(package.public_id),
        resource_public_id=resource.id,
        starts_at=future_tuesday(),
        customer_payload=make_customer_payload(),
        idempotency_key="status-full-package",
    )
    booking = Booking.objects.get(public_id=result["booking_public_id"])
    booking.status = Booking.Status.CONFIRMED
    booking.confirmed_at = booking.starts_at
    booking.save(update_fields=["status", "confirmed_at", "updated_at"])

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["booking_status"] == Booking.Status.CONFIRMED
    assert payload["service"]["selection_type"] == Booking.BookingType.FULL_PACKAGE
    assert payload["schedule"]["duration_minutes"] == 300
    assert "<b>" not in str(payload)
    assert str(booking.id) not in str(payload)


@pytest.mark.django_db
def test_booking_status_endpoint_generic_404_for_invalid_and_missing_ids():
    client = Client()

    malformed = client.get("/api/bookings/status/not-a-uuid/", secure=True)
    missing = client.get("/api/bookings/status/00000000-0000-4000-8000-000000000000/", secure=True)

    assert malformed.status_code == 404
    assert missing.status_code == 404
    assert malformed.json() == missing.json()
    assert malformed.json() == {"detail": "Booking status is unavailable."}
