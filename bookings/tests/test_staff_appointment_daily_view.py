import pytest
from django.test import Client

from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource
from bookings.tests.test_staff_portal_helpers import mark_confirmed, staff_login


@pytest.mark.django_db(transaction=True)
def test_daily_spreadsheet_view_is_sorted_capacity_aware_and_pii_safe():
    resource = make_resource()
    service = __import__("bookings.models").models.Service.objects.create(
        name="<script>Soft Glam</script>",
        slug="staff-soft-glam",
        category="makeup",
        duration_minutes=60,
        base_price="2500.00",
    )
    later = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id)],
        resource_public_id=resource.id,
        starts_at=future_monday().replace(hour=8),
        customer_payload=make_customer_payload(),
        idempotency_key="staff-daily-later",
    )
    earlier = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id)],
        resource_public_id=resource.id,
        starts_at=future_monday(),
        customer_payload=make_customer_payload(),
        idempotency_key="staff-daily-earlier",
    )
    from bookings.models import Booking

    mark_confirmed(Booking.objects.get(public_id=later["booking_public_id"]))
    mark_confirmed(Booking.objects.get(public_id=earlier["booking_public_id"]))

    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.get("/api/staff/bookings/schedule/?date=2030-06-03", secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert payload["local_date"] == "2030-06-03"
    assert payload["day_type"] == "normal"
    assert payload["capacity"]["max_clients"] == 5
    assert payload["capacity"]["booked_clients"] == 2
    assert [row["start_time_eat"] for row in payload["appointments"]] == sorted(
        row["start_time_eat"] for row in payload["appointments"]
    )
    body = str(payload)
    assert "<script" not in body.lower()
    assert "grace@example.com" not in body.lower()
    assert "+254" not in body
    assert '"id"' not in body.lower()
