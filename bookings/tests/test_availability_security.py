from datetime import date, datetime, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import BlackoutPeriod, Booking
from bookings.tests.factories import create_booking, create_service_resource_customer


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


class BrokenRedis:
    def incr(self, _key):
        raise ConnectionError("redis unavailable")


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expiries = {}

    def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key, ttl):
        self.expiries[key] = ttl


@pytest.mark.django_db
def test_excessive_date_range_is_rejected_without_unbounded_query():
    service, resource, _customer = create_service_resource_customer()
    start = timezone.localdate()

    with pytest.raises(ValidationError):
        _service().get_available_slots(service.id, start, start + timedelta(days=45), resource_id=resource.id)


@pytest.mark.django_db
def test_invalid_or_inactive_service_returns_generic_unavailable_error():
    service, resource, _customer = create_service_resource_customer()
    service.is_active = False
    service.save(update_fields=["is_active", "updated_at"])

    with pytest.raises(ValidationError) as exc:
        _service().get_available_slots(service.id, date(2026, 6, 1), date(2026, 6, 1), resource_id=resource.id)

    assert "availability unavailable" in str(exc.value).lower()
    assert str(service.id) not in str(exc.value)


@pytest.mark.django_db
def test_response_contains_no_customer_pii_or_internal_booking_id(caplog):
    service, resource, customer = create_service_resource_customer()
    day = date(2026, 6, 1)
    booking = create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=timezone.make_aware(datetime(2026, 6, 1, 9, 0), timezone=timezone.get_current_timezone()),
        ends_at=timezone.make_aware(datetime(2026, 6, 1, 10, 0), timezone=timezone.get_current_timezone()),
        status=Booking.Status.CONFIRMED,
    )

    result = _service().get_available_slots(service.id, day, day, resource_id=resource.id)

    payload = str(result) + caplog.text
    assert customer.phone_redacted not in payload
    assert customer.email_redacted not in payload
    assert str(booking.id) not in payload


@pytest.mark.django_db
def test_malicious_stored_strings_are_not_reflected_in_availability_response():
    service, resource, _customer = create_service_resource_customer()
    service.name = "<script>alert(1)</script>"
    service.save(update_fields=["name", "updated_at"])
    BlackoutPeriod.objects.create(
        resource=resource,
        starts_at=timezone.now() + timedelta(days=3),
        ends_at=timezone.now() + timedelta(days=3, hours=1),
        reason="<img src=x onerror=alert(1)>",
    )

    result = _service().get_available_slots(service.id, date(2026, 6, 1), date(2026, 6, 1), resource_id=resource.id)

    assert "<script" not in str(result)
    assert "onerror" not in str(result)


@pytest.mark.django_db
def test_redis_availability_counter_uses_ttl_and_redis_outage_fails_safely():
    service, resource, _customer = create_service_resource_customer()
    redis = FakeRedis()

    _service().get_available_slots(
        service.id,
        date(2026, 6, 1),
        date(2026, 6, 1),
        resource_id=resource.id,
        request_context={"redis_client": redis, "request_id": "req-redacted"},
    )
    _service().get_available_slots(
        service.id,
        date(2026, 6, 1),
        date(2026, 6, 1),
        resource_id=resource.id,
        request_context={"redis_client": BrokenRedis()},
    )

    assert redis.values["booking:availability:requests:10m"] == 1
    assert redis.expiries["booking:availability:requests:10m"] > 0
