from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from bookings.models import BookingPolicy
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


class FakeRedis:
    def __init__(self, values=None):
        self.values = values or {}
        self.expiries = {}

    def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key, ttl):
        self.expiries[key] = ttl

    def get(self, key):
        # Mirrors a real Redis client: values are always returned as strings.
        value = self.values.get(key)
        return None if value is None else str(value)


class BrokenRedis:
    def incr(self, _key):
        raise ConnectionError("down")


def _service():
    try:
        from bookings.services.holds import BookingHoldService
    except ImportError as exc:
        pytest.fail(f"BookingHoldService missing: {exc}")
    return BookingHoldService


def _starts():
    return datetime.combine(date(2026, 6, 1), time(9, 0), tzinfo=NAIROBI)


@pytest.mark.django_db
def test_hold_attempt_counters_have_ttl_and_abuse_mode_shortens_hold_ttl():
    service, resource, _customer = create_service_resource_customer()
    BookingPolicy.objects.create(default_hold_minutes=10, abuse_hold_minutes=3)
    redis = FakeRedis({"booking:holds:created:10m": 20, "booking:holds:confirmed:10m": 0})

    result = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload={"full_name": "Grace", "email": "grace@example.com", "phone": "+254712345678"},
        idempotency_key="abuse-ttl",
        request_context={"redis_client": redis, "ip_hash": "ip-redacted", "request_id": "req-redacted"},
    )

    assert redis.expiries["booking:holds:attempted:10m"] > 0
    assert redis.expiries["booking:holds:created:10m"] > 0
    assert result["hold_ttl_minutes"] == 3


@pytest.mark.django_db
def test_redis_outage_does_not_crash_hold_creation():
    service, resource, _customer = create_service_resource_customer()

    result = _service().create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload={"full_name": "Grace", "email": "grace@example.com", "phone": "+254712345678"},
        idempotency_key="redis-down-safe",
        request_context={"redis_client": BrokenRedis(), "request_id": "req-redacted"},
    )

    assert result["status"] == "held"
