from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking
from bookings.services.circuit_breaker import BookingCircuitBreaker
from bookings.services.public_lookup import BookingLookupError, public_booking_summary
from bookings.tests.factories import create_booking

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_attacker_cannot_double_book_same_resource_under_overlap_race():
    starts = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=7)
    booking = create_booking(starts_at=starts, ends_at=starts + timedelta(hours=1), status=Booking.Status.CONFIRMED)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            create_booking(
                resource=booking.resource,
                starts_at=starts + timedelta(minutes=1),
                ends_at=starts + timedelta(minutes=30),
                status=Booking.Status.CONFIRMED,
            )


@pytest.mark.django_db
def test_public_lookup_uses_generic_errors_and_no_internal_id_leakage():
    booking = create_booking()

    with pytest.raises(BookingLookupError):
        public_booking_summary(str(booking.public_id), phone="+254700999999")

    with pytest.raises(BookingLookupError):
        public_booking_summary("00000000-0000-0000-0000-000000000000", phone="+254700999999")

    summary = public_booking_summary(str(booking.public_id), phone="+254712345678")
    assert "id" not in summary
    assert summary["public_id"] == str(booking.public_id)


@pytest.mark.django_db
def test_booking_creation_rejects_naive_datetime_and_raw_refund_path():
    booking = create_booking()
    booking.starts_at = booking.starts_at.replace(tzinfo=None)

    with pytest.raises(ValidationError):
        booking.full_clean()

    assert not hasattr(booking, "refund")
    assert not hasattr(booking, "request_refund")


def test_circuit_breaker_uses_ttl_and_fails_safely(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.ttls = {}
            self.values = {}

        def incr(self, key):
            self.values[key] = self.values.get(key, 0) + 1
            return self.values[key]

        def expire(self, key, ttl):
            self.ttls[key] = ttl
            return True

        def ttl(self, key):
            return self.ttls.get(key, -1)

    fake = FakeRedis()
    breaker = BookingCircuitBreaker(redis_client=fake)
    breaker.incr("booking:holds_created:10m")

    assert fake.ttl("booking:holds_created:10m") > 0

    class BrokenRedis:
        def incr(self, _key):
            raise ConnectionError("redis down")

    broken = BookingCircuitBreaker(redis_client=BrokenRedis())
    assert broken.mode_for_context() == BookingCircuitBreaker.Mode.LOCKDOWN
