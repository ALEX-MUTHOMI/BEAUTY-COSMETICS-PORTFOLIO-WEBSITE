from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from bookings.models import Booking, BookingAuditEvent
from bookings.tests.factories import create_booking, create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _expiry_service():
    try:
        from bookings.services.hold_expiry import BookingHoldExpiryService
    except ImportError as exc:
        pytest.fail(f"BookingHoldExpiryService missing: {exc}")
    return BookingHoldExpiryService


def _starts(hour=9):
    return datetime.combine(date(2026, 6, 1), time(hour, 0), tzinfo=NAIROBI).astimezone(ZoneInfo("UTC"))


@pytest.mark.django_db
def test_expire_stale_holds_is_idempotent_audited_and_does_not_touch_payment_pending():
    service, resource, customer = create_service_resource_customer()
    expired = create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_starts(9),
        ends_at=_starts(10),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
        idempotency_key="expired-hold",
    )
    active = create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_starts(10),
        ends_at=_starts(11),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() + timedelta(minutes=10),
        idempotency_key="active-hold",
    )
    payment_pending = create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_starts(11),
        ends_at=_starts(12),
        status=Booking.Status.PAYMENT_PENDING,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
        idempotency_key="payment-pending-hold",
    )

    first = _expiry_service().expire_stale_holds(limit=10)
    second = _expiry_service().expire_stale_holds(limit=10)

    expired.refresh_from_db()
    active.refresh_from_db()
    payment_pending.refresh_from_db()
    assert first == 1
    assert second == 0
    assert expired.status == Booking.Status.EXPIRED
    assert active.status == Booking.Status.HELD
    assert payment_pending.status == Booking.Status.PAYMENT_PENDING
    assert BookingAuditEvent.objects.filter(booking=expired, new_status=Booking.Status.EXPIRED).exists()


@pytest.mark.django_db
def test_expired_hold_cleanup_frees_availability_slot():
    service, resource, customer = create_service_resource_customer()
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_starts(9),
        ends_at=_starts(10),
        status=Booking.Status.HELD,
        hold_expires_at=timezone.now() - timedelta(minutes=1),
        idempotency_key="expired-frees-slot",
    )

    _expiry_service().expire_stale_holds(limit=10)

    from bookings.services.availability import AvailabilityService

    result = AvailabilityService.get_available_slots(
        service.id, date(2026, 6, 1), date(2026, 6, 1), resource_id=resource.id
    )
    assert any("09:00:00+03:00" in slot["starts_at"] for slot in result[0]["slots"])
