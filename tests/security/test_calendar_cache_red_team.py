"""Red-team: calendar cache must not leak, poison, or serve stale availability."""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.test import Client

from bookings.models import Booking
from bookings.services.booking_calendar import BookingCalendarService
from bookings.services.calendar_cache import (
    CACHE_KEY_PREFIX,
    CalendarCache,
    bump_capacity_generation,
    invalidate_calendar_capacity_for_transition,
)
from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


class BrokenRedis:
    def get(self, _key):
        raise ConnectionError("redis unavailable")

    def setex(self, *_args, **_kwargs):
        raise ConnectionError("redis unavailable")

    def mget(self, _keys):
        raise ConnectionError("redis unavailable")

    def incr(self, _key):
        raise ConnectionError("redis unavailable")


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def setex(self, key, _ttl, value):
        self.values[key] = value

    def mget(self, keys):
        return [self.values.get(key) for key in keys]

    def incr(self, key):
        self.values[key] = int(self.values.get(key, 0)) + 1
        return self.values[key]


@pytest.mark.django_db
def test_calendar_survives_redis_outage_without_5xx():
    service, _resource, _customer = create_service_resource_customer()
    context = {"redis_client": BrokenRedis()}

    payload = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        request_context=context,
    )

    assert len(payload["days"]) == 8


@pytest.mark.django_db
def test_calendar_cache_key_never_embeds_raw_user_input():
    service, _resource, _customer = create_service_resource_customer()
    offered_dates = [date(2030, 6, 3)]
    malicious_resource = "../../etc/passwd"

    cache_key = CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=offered_dates,
        resource_id=malicious_resource,
        redis_client=FakeRedis(),
    )

    assert cache_key is not None
    assert malicious_resource not in cache_key
    assert cache_key.startswith(CACHE_KEY_PREFIX)


@pytest.mark.django_db
def test_hold_creation_invalidates_cached_calendar_capacity():
    service, resource, _customer = create_service_resource_customer()
    context = {"redis_client": FakeRedis()}

    before = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date="2030-06-03",
        end_date="2030-06-09",
        request_context=context,
    )
    cached = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date="2030-06-03",
        end_date="2030-06-09",
        request_context=context,
    )
    assert cached == before

    starts_at = datetime.combine(date(2030, 6, 3), time(9, 0), tzinfo=NAIROBI)
    BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=starts_at,
        customer_payload={"full_name": "Ada", "email": "ada@example.com", "phone": "+254712345678"},
        idempotency_key="calendar-cache-invalidate",
        request_context=context,
    )

    after = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date="2030-06-03",
        end_date="2030-06-09",
        request_context=context,
    )
    target_day = next(day for day in after["days"] if day["date"] == "2030-06-03")
    assert target_day["capacity"]["booked"] >= 1
    assert target_day != next(day for day in before["days"] if day["date"] == "2030-06-03")


@pytest.mark.django_db
def test_capacity_generation_bump_forces_cache_miss():
    service, _resource, _customer = create_service_resource_customer()
    offered_dates = [date(2030, 6, 3)]
    redis = FakeRedis()

    key_before = CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=offered_dates,
        redis_client=redis,
    )
    bump_capacity_generation(date(2030, 6, 3), redis_client=redis)
    key_after = CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=offered_dates,
        redis_client=redis,
    )

    assert key_before != key_after


@pytest.mark.django_db
def test_calendar_api_cache_hit_does_not_skip_authz_or_throttle_headers(client):
    service, _resource, _customer = create_service_resource_customer()

    response = client.get(
        "/api/bookings/calendar/",
        {"selection_type": "normal", "service_public_id": str(service.id)},
        secure=True,
    )

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"


@pytest.mark.django_db
def test_calendar_cache_does_not_mask_inactive_service_as_available():
    service, _resource, _customer = create_service_resource_customer()
    service.is_active = False
    service.save(update_fields=["is_active", "updated_at"])

    response = Client().get(
        "/api/bookings/calendar/",
        {"selection_type": "normal", "service_public_id": str(service.id)},
        secure=True,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Calendar unavailable."


@pytest.mark.django_db
def test_blocking_status_transition_bumps_capacity_generation():
    service, _resource, _customer = create_service_resource_customer()
    local_date = date(2030, 6, 4)
    redis = FakeRedis()
    key_before = CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=[local_date],
        redis_client=redis,
    )

    invalidate_calendar_capacity_for_transition(
        old_status=Booking.Status.CONFIRMED,
        new_status=Booking.Status.CANCELLED_BY_BUSINESS,
        local_date=local_date,
        redis_client=redis,
    )
    key_after = CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=[local_date],
        redis_client=redis,
    )

    assert key_before != key_after
