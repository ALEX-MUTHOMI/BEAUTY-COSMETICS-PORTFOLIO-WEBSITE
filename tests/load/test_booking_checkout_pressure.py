from concurrent.futures import ThreadPoolExecutor

import pytest
from django.core.exceptions import ValidationError
from django.db import connections

from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expiries = {}

    def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key, ttl):
        self.expiries[key] = ttl


class BrokenRedis:
    def incr(self, _key):
        raise ConnectionError("down")


@pytest.mark.django_db(transaction=True)
def test_repeated_checkout_pressure_creates_one_session_and_uses_ttl_counters():
    booking = _held_booking(key="checkout-pressure-hold")
    redis = FakeRedis()

    def attempt(_index):
        try:
            return _contract_service().create_checkout_for_held_booking(
                booking_public_id=booking.public_id,
                idempotency_key="checkout-pressure-key",
                request_context={"redis_client": redis, "request_id": "req-redacted"},
            )
        except ValidationError as exc:
            return {"error": str(exc)}
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(attempt, range(50)))

    assert len({result["checkout_public_id"] for result in results if "checkout_public_id" in result}) == 1
    assert CheckoutSession.objects.count() == 1
    assert redis.expiries["booking:checkout:attempted:10m"] > 0
    assert redis.expiries["booking:checkout:created:10m"] > 0
    assert redis.expiries["booking:checkout:replayed:10m"] > 0


@pytest.mark.django_db
def test_redis_outage_does_not_crash_checkout_contract():
    booking = _held_booking(key="checkout-redis-down")

    result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="checkout-redis-down-key",
        request_context={"redis_client": BrokenRedis()},
    )

    assert result["next_action"] == "initiate_payment"
