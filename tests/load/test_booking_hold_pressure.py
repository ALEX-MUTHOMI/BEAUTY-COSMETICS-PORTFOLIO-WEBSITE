from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.db import connections

from bookings.models import Booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


@pytest.mark.django_db(transaction=True)
def test_fifty_same_slot_hold_attempts_create_one_active_hold():
    service, resource, _customer = create_service_resource_customer()
    starts_at = datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI)

    def attempt(index):
        try:
            return _service().create_hold(
                service_public_id=service.id,
                resource_public_id=resource.id,
                starts_at=starts_at,
                customer_payload={
                    "full_name": f"User {index}",
                    "email": f"user{index}@example.com",
                    "phone": f"+25471235{index:04d}",
                },
                idempotency_key=f"load-hold-{index}",
            )
        except ValidationError:
            return {"error": "slot_unavailable"}
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(attempt, range(50)))

    assert sum(1 for result in results if result.get("status") == Booking.Status.HELD) == 1
    assert Booking.objects.filter(status=Booking.Status.HELD).count() == 1
