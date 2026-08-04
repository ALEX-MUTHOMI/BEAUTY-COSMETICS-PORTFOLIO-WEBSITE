from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.db import connections

from bookings.models import BookableResource, Booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


def _payload(index):
    return {"full_name": f"Customer {index}", "email": f"customer{index}@example.com", "phone": f"+25471234{index:04d}"}


def _starts(hour=9):
    return datetime.combine(date(2026, 6, 1), time(hour, 0), tzinfo=NAIROBI)


@pytest.mark.django_db(transaction=True)
def test_ten_concurrent_same_slot_attempts_have_exactly_one_winner():
    service, resource, _customer = create_service_resource_customer()

    def attempt(index):
        try:
            return _service().create_hold(
                service_public_id=service.id,
                resource_public_id=resource.id,
                starts_at=_starts(),
                customer_payload=_payload(index),
                idempotency_key=f"race-{index}",
            )
        except ValidationError as exc:
            return {"error": str(exc)}
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(attempt, range(10)))

    winners = [result for result in results if result.get("status") == Booking.Status.HELD]
    losers = [result for result in results if "error" in result]
    assert len(winners) == 1
    assert len(losers) == 9
    assert Booking.objects.filter(status=Booking.Status.HELD).count() == 1
    assert all("unavailable" in loser["error"].lower() for loser in losers)


@pytest.mark.django_db
def test_adjacent_slots_and_different_resources_are_allowed():
    service, resource, _customer = create_service_resource_customer()
    other = BookableResource.objects.create(name="Second chair", resource_type="chair")

    first = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(hour=9),
        customer_payload=_payload(1),
        idempotency_key="adjacent-1",
    )
    adjacent = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(hour=10),
        customer_payload=_payload(2),
        idempotency_key="adjacent-2",
    )
    parallel = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=other.id,
        starts_at=_starts(hour=9),
        customer_payload=_payload(3),
        idempotency_key="different-resource",
    )

    assert first["booking_public_id"] != adjacent["booking_public_id"]
    assert first["booking_public_id"] != parallel["booking_public_id"]
