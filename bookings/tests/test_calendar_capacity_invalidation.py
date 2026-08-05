"""Contract: capacity-gen invalidation across hold / expire / confirm / cancel."""

from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from bookings.models import Booking
from bookings.services.booking_calendar import BookingCalendarService
from bookings.services.calendar_cache import CalendarCache
from bookings.services.hold_expiry import BookingHoldExpiryService
from bookings.services.holds import BookingHoldService
from bookings.services.state_machine import transition_booking
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


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


def _cache_key_for(service, local_date: date, redis: FakeRedis) -> str:
    return CalendarCache.build_key(
        selection_public_id=service.id,
        offered_dates=[local_date],
        redis_client=redis,
    )


def _as_utc(local_dt: datetime) -> datetime:
    return local_dt.astimezone(dt_timezone.utc)


@pytest.mark.django_db
def test_hold_create_bumps_capacity_generation():
    service, resource, _customer = create_service_resource_customer()
    redis = FakeRedis()
    local_date = date(2030, 7, 1)  # Tuesday
    before = _cache_key_for(service, local_date, redis)

    BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=datetime.combine(local_date, time(9, 0), tzinfo=NAIROBI),
        customer_payload={"full_name": "Ada", "email": "ada-inv@example.com", "phone": "+254711111111"},
        idempotency_key="capacity-inv-hold",
        request_context={"redis_client": redis},
    )

    after = _cache_key_for(service, local_date, redis)
    assert before != after


@pytest.mark.django_db
def test_hold_expire_bumps_capacity_generation():
    service, resource, customer = create_service_resource_customer()
    redis = FakeRedis()
    local_date = date(2030, 7, 2)
    starts = datetime.combine(local_date, time(10, 0), tzinfo=NAIROBI)
    ends = starts + timedelta(minutes=service.duration_minutes)
    Booking.objects.create(
        customer_profile=customer,
        service=service,
        resource=resource,
        starts_at=_as_utc(starts),
        ends_at=_as_utc(ends),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
        idempotency_key="capacity-inv-expire",
        local_booking_date=local_date,
    )
    before = _cache_key_for(service, local_date, redis)

    expired = BookingHoldExpiryService.expire_stale_holds(limit=10, redis_client=redis)
    assert expired >= 1

    after = _cache_key_for(service, local_date, redis)
    assert before != after


@pytest.mark.django_db
def test_cancel_transition_bumps_capacity_generation():
    service, resource, customer = create_service_resource_customer()
    redis = FakeRedis()
    local_date = date(2030, 7, 3)
    starts = datetime.combine(local_date, time(11, 0), tzinfo=NAIROBI)
    ends = starts + timedelta(minutes=service.duration_minutes)
    booking = Booking.objects.create(
        customer_profile=customer,
        service=service,
        resource=resource,
        starts_at=_as_utc(starts),
        ends_at=_as_utc(ends),
        status=Booking.Status.CONFIRMED,
        confirmed_at=timezone.now(),
        idempotency_key="capacity-inv-cancel",
        local_booking_date=local_date,
    )
    before = _cache_key_for(service, local_date, redis)

    # Inject redis into transition by patching invalidate path via monkeypatch-like
    # direct call: transition_booking uses default redis; also bump via FakeRedis
    # by wrapping invalidate used inside state_machine.
    from bookings.services import state_machine as sm

    original = sm.invalidate_calendar_capacity_for_transition

    def _invalidate(**kwargs):
        kwargs = {**kwargs, "redis_client": redis}
        return original(**kwargs)

    sm.invalidate_calendar_capacity_for_transition = _invalidate
    try:
        transition_booking(booking, Booking.Status.CANCELLED_BY_BUSINESS, actor_type="staff", reason="test")
    finally:
        sm.invalidate_calendar_capacity_for_transition = original

    after = _cache_key_for(service, local_date, redis)
    assert before != after


@pytest.mark.django_db
def test_confirm_from_payment_pending_keeps_blocking_then_cancel_frees_calendar():
    """Payment_pending → confirmed stays blocking; cancel must refresh calendar capacity."""
    service, resource, customer = create_service_resource_customer()
    redis = FakeRedis()
    local_date = date(2030, 6, 3)  # Monday
    context = {"redis_client": redis}

    starts = datetime.combine(local_date, time(9, 0), tzinfo=NAIROBI)
    ends = starts + timedelta(minutes=service.duration_minutes)
    booking = Booking.objects.create(
        customer_profile=customer,
        service=service,
        resource=resource,
        starts_at=_as_utc(starts),
        ends_at=_as_utc(ends),
        status=Booking.Status.PAYMENT_PENDING,
        idempotency_key="capacity-inv-confirm-cal",
        local_booking_date=local_date,
    )

    before = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date="2030-06-03",
        end_date="2030-06-09",
        request_context=context,
    )
    booked_before = next(day for day in before["days"] if day["date"] == "2030-06-03")["capacity"]["booked"]
    assert booked_before >= 1

    from bookings.services import state_machine as sm

    original = sm.invalidate_calendar_capacity_for_transition

    def _invalidate(**kwargs):
        return original(**{**kwargs, "redis_client": redis})

    sm.invalidate_calendar_capacity_for_transition = _invalidate
    try:
        transition_booking(booking, Booking.Status.CONFIRMED, actor_type="system", reason="paid")
        transition_booking(booking, Booking.Status.CANCELLED_BY_BUSINESS, actor_type="staff", reason="test")
    finally:
        sm.invalidate_calendar_capacity_for_transition = original

    after = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date="2030-06-03",
        end_date="2030-06-09",
        request_context=context,
    )
    booked_after = next(day for day in after["days"] if day["date"] == "2030-06-03")["capacity"]["booked"]
    assert booked_after < booked_before
