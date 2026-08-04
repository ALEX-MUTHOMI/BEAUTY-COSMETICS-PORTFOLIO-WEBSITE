"""Staff desk reschedule queue + move endpoint (no customer OTP)."""

from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.test import Client
from django.utils import timezone

from bookings.services.rescheduling import GENERIC_RESCHEDULE_ERROR, BookingRescheduleService
from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import mark_confirmed, staff_login
from bookings.tests.time_helpers import make_utc_from_eat, valid_business_start_utc, valid_reschedule_start_utc

EAT = ZoneInfo("Africa/Nairobi")
UTC = ZoneInfo("UTC")


def _near_business_start_utc(*, days_ahead=3):
    """Next open-desk 10:00 EAT at least days_ahead from now (skip Sunday)."""
    cursor = timezone.now().astimezone(EAT) + timedelta(days=days_ahead)
    while cursor.weekday() == 6:
        cursor += timedelta(days=1)
    return cursor.replace(hour=10, minute=0, second=0, microsecond=0).astimezone(UTC)


@pytest.mark.django_db
def test_staff_reschedule_queue_requires_staff_session():
    anon = Client().get("/api/staff/bookings/reschedule-queue/", secure=True)
    assert anon.status_code == 403


@pytest.mark.django_db
def test_staff_reschedule_queue_lists_confirmed_and_requested_moves():
    confirmed = mark_confirmed(create_booking(status="held", starts_at=_near_business_start_utc(days_ahead=2)))
    requested = create_booking(
        status="reschedule_requested",
        starts_at=_near_business_start_utc(days_ahead=4),
    )

    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.get("/api/staff/bookings/reschedule-queue/", secure=True)
    assert response.status_code == 200
    payload = response.json()
    ids = {row["public_booking_id"] for row in payload["appointments"]}
    assert str(confirmed.public_id) in ids
    assert str(requested.public_id) in ids
    assert payload["count"] >= 2


@pytest.mark.django_db(transaction=True)
def test_staff_reschedule_endpoint_moves_confirmed_booking_without_otp():
    booking = mark_confirmed(create_booking(status="held", starts_at=valid_business_start_utc()))
    new_start = valid_reschedule_start_utc()

    client = Client()
    staff_login(client, permissions=["confirm_staff_attendance", "view_staff_booking"])
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/reschedule/",
        data={"requested_starts_at": new_start.isoformat(), "reason": "Client asked to move"},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 200, response.content
    body = response.json()
    assert body["booking_status"] == "confirmed"
    assert body["start_time_eat"] == "10:00"

    booking.refresh_from_db()
    assert booking.starts_at == new_start
    assert booking.reschedule_count == 1


@pytest.mark.django_db
def test_staff_reschedule_endpoint_rejects_without_permission():
    booking = mark_confirmed(create_booking(status="held", starts_at=valid_business_start_utc()))
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/reschedule/",
        data={"requested_starts_at": valid_reschedule_start_utc().isoformat()},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_staff_reschedule_rejects_sunday_and_after_hours():
    booking = mark_confirmed(create_booking(status="held", starts_at=valid_business_start_utc()))
    sunday = make_utc_from_eat(2030, 6, 9, 10, 0)

    with pytest.raises(ValidationError, match=GENERIC_RESCHEDULE_ERROR):
        BookingRescheduleService.staff_reschedule(
            booking_public_id=str(booking.public_id),
            requested_starts_at=sunday,
            reason="bad sunday",
        )

    after_hours = make_utc_from_eat(2030, 6, 6, 3, 0)
    with pytest.raises(ValidationError, match=GENERIC_RESCHEDULE_ERROR):
        BookingRescheduleService.staff_reschedule(
            booking_public_id=str(booking.public_id),
            requested_starts_at=after_hours,
            reason="too early",
        )


@pytest.mark.django_db
def test_staff_reschedule_endpoint_rejects_invalid_payload():
    booking = mark_confirmed(create_booking(status="held", starts_at=valid_business_start_utc()))
    client = Client()
    staff_login(client, permissions=["confirm_staff_attendance"])
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/reschedule/",
        data={"requested_starts_at": "not-a-date"},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 400
