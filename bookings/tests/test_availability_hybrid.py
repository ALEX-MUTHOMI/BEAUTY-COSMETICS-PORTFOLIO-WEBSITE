"""Hybrid availability: duration-stepped packages + dense singles."""

from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from bookings.models import Booking, FullPackage
from bookings.services.availability import AvailabilityService
from bookings.tests.factories import create_booking, create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _utc_on(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), tzinfo=NAIROBI).astimezone(ZoneInfo("UTC"))


@pytest.mark.django_db
def test_glow_package_offers_stepped_anchors_only():
    _, resource, _ = create_service_resource_customer()
    package = FullPackage.objects.create(
        name="Glow Package",
        slug=f"glow-{datetime.now().timestamp()}",
        duration_minutes=180,
        price_amount=Decimal("8500.00"),
        buffer_after_minutes=0,
    )
    # Tuesday package day
    day = date(2026, 6, 2)

    result = AvailabilityService.get_full_package_available_slots(
        str(package.public_id),
        day,
        day,
        resource_id=resource.id,
    )
    starts = [slot["starts_at"][11:16] for slot in result[0]["slots"]]
    assert starts == ["07:00", "10:00", "13:00"]
    assert "08:30" not in starts


@pytest.mark.django_db
def test_classic_package_anchors_four_hour_blocks():
    _, resource, _ = create_service_resource_customer()
    package = FullPackage.objects.create(
        name="Classic Full Package",
        slug=f"classic-{datetime.now().timestamp()}",
        duration_minutes=240,
        price_amount=Decimal("12000.00"),
        buffer_after_minutes=0,
    )
    day = date(2026, 6, 3)  # Wednesday

    result = AvailabilityService.get_full_package_available_slots(
        str(package.public_id),
        day,
        day,
        resource_id=resource.id,
    )
    starts = [slot["starts_at"][11:16] for slot in result[0]["slots"]]
    assert starts == ["07:00", "11:00", "15:00"]


@pytest.mark.django_db
def test_package_after_morning_booking_keeps_later_anchors():
    service, resource, customer = create_service_resource_customer()
    package = FullPackage.objects.create(
        name="Glow Package",
        slug=f"glow-booked-{datetime.now().timestamp()}",
        duration_minutes=180,
        price_amount=Decimal("8500.00"),
        buffer_after_minutes=0,
    )
    day = date(2026, 6, 2)
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 7),
        ends_at=_utc_on(day, 10),
        status=Booking.Status.CONFIRMED,
        booking_type=Booking.BookingType.FULL_PACKAGE,
        idempotency_key="pkg-morning",
    )

    result = AvailabilityService.get_full_package_available_slots(
        str(package.public_id),
        day,
        day,
        resource_id=resource.id,
    )
    starts = [slot["starts_at"][11:16] for slot in result[0]["slots"]]
    assert starts == ["10:00", "13:00"]


@pytest.mark.django_db
def test_single_dense_slots_fill_free_gaps():
    service, resource, customer = create_service_resource_customer()
    service.duration_minutes = 45
    service.buffer_before_minutes = 0
    service.buffer_after_minutes = 15
    service.save(
        update_fields=[
            "duration_minutes",
            "buffer_before_minutes",
            "buffer_after_minutes",
            "updated_at",
        ]
    )
    day = date(2026, 6, 1)  # Monday
    create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=_utc_on(day, 9),
        ends_at=_utc_on(day, 9, 45),
        status=Booking.Status.CONFIRMED,
        idempotency_key="single-gap",
    )

    result = AvailabilityService.get_available_slots(service.id, day, day, resource_id=resource.id)
    starts = [slot["starts_at"][11:16] for slot in result[0]["slots"]]
    assert "07:00" in starts
    assert "09:00" not in starts
    # After 09:00–09:45 + 15m after-buffer, next free window starts ~10:00
    assert any(s >= "10:00" for s in starts)
