from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


def _starts_at(day=date(2026, 6, 1), hour=9):
    return datetime.combine(day, time(hour, 0), tzinfo=NAIROBI)


def _payload(**overrides):
    data = {"full_name": "Grace Wanjiku", "email": "grace@example.com", "phone": "+254712345678"}
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_create_hold_uses_server_side_duration_policy_and_utc_persistence():
    service, resource, _customer = create_service_resource_customer()
    service.duration_minutes = 60
    service.buffer_after_minutes = 15
    service.save(update_fields=["duration_minutes", "buffer_after_minutes", "updated_at"])

    result = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts_at(),
        customer_payload=_payload(),
        idempotency_key="hold-service-1",
    )

    booking = Booking.objects.get(public_id=result["booking_public_id"])
    assert result["status"] == Booking.Status.HELD
    assert result["next_action"] == "checkout_required"
    assert booking.starts_at.tzinfo is not None
    assert booking.starts_at.hour == 6
    assert booking.ends_at.hour == 7
    assert booking.hold_expires_at > timezone.now()
    assert result["ends_at"].endswith("10:00:00+03:00")
    assert result["hold_expires_at"].endswith("+03:00")


@pytest.mark.django_db
def test_sunday_and_out_of_hours_hold_are_rejected_generically():
    service, resource, _customer = create_service_resource_customer()

    with pytest.raises(ValidationError) as sunday:
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=_starts_at(day=date(2026, 6, 7), hour=9),
            customer_payload=_payload(),
            idempotency_key="hold-sunday",
        )
    with pytest.raises(ValidationError) as late:
        _service().create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=_starts_at(hour=20),
            customer_payload=_payload(),
            idempotency_key="hold-late",
        )

    assert "unavailable" in str(sunday.value).lower()
    assert "unavailable" in str(late.value).lower()


@pytest.mark.django_db
def test_active_hold_blocks_availability_immediately():
    service, resource, _customer = create_service_resource_customer()
    _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts_at(hour=9),
        customer_payload=_payload(),
        idempotency_key="hold-blocks-availability",
    )

    from bookings.services.availability import AvailabilityService

    result = AvailabilityService.get_available_slots(
        service.id, date(2026, 6, 1), date(2026, 6, 1), resource_id=resource.id
    )

    starts = [slot["starts_at"] for slot in result[0]["slots"]]
    assert not any("09:00:00+03:00" in value for value in starts)
