import pytest
from django.test import Client

from bookings.models import Booking, FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_tuesday, make_customer_payload, make_resource
from bookings.tests.test_staff_portal_helpers import mark_confirmed, staff_booking_url, staff_login


@pytest.mark.django_db(transaction=True)
def test_staff_detail_supports_full_package_without_internal_or_raw_pii_leakage():
    resource = make_resource()
    package = FullPackage.objects.create(
        name="<b>Bridal Package</b>",
        slug="staff-bridal-package",
        duration_minutes=300,
        price_amount="15000.00",
    )
    result = BookingHoldService.create_full_package_hold(
        full_package_public_id=str(package.public_id),
        resource_public_id=resource.id,
        starts_at=future_tuesday(),
        customer_payload=make_customer_payload(),
        idempotency_key="staff-detail-full-package",
    )
    booking = mark_confirmed(Booking.objects.get(public_id=result["booking_public_id"]))

    client = Client()
    staff_login(client, permissions=["view_staff_booking"])
    response = client.get(staff_booking_url(booking), secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["booking_type"] == Booking.BookingType.FULL_PACKAGE
    assert payload["service_summary"] == "Bridal Package"
    assert "payment_summary" not in payload
    body = str(payload)
    assert "<b>" not in body
    assert "grace@example.com" not in body.lower()
    assert str(booking.id) not in body


@pytest.mark.django_db
def test_invalid_staff_booking_detail_is_generic_404():
    client = Client()
    staff_login(client, permissions=["view_staff_booking"])
    response = client.get("/api/staff/bookings/not-a-real-id/", secure=True)
    assert response.status_code == 404
    assert response.json() == {"detail": "Staff booking record is unavailable."}
