from datetime import time
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import BookableResource, BookingPolicy, BusinessHours, Service


@pytest.mark.django_db
def test_service_catalog_enforces_duration_and_server_side_prices():
    service = Service.objects.create(
        name="Executive makeup",
        slug="executive-makeup",
        category="makeup",
        duration_minutes=90,
        base_price=Decimal("2500.00"),
        urgent_fee=Decimal("500.00"),
        sunday_surcharge=Decimal("300.00"),
    )

    assert service.is_active is True
    assert service.duration_minutes == 90

    invalid = Service(
        name="Unsafe",
        slug="unsafe",
        category="makeup",
        duration_minutes=15,
        base_price=Decimal("-1.00"),
    )
    with pytest.raises(ValidationError):
        invalid.full_clean()


@pytest.mark.django_db
def test_bookable_resource_and_default_business_hours_policy():
    resource = BookableResource.objects.create(name="Massage room 1", resource_type=BookableResource.Type.ROOM)
    BusinessHours.create_default_week(resource=resource)

    assert BusinessHours.objects.filter(resource=resource).count() == 7
    sunday = BusinessHours.objects.get(resource=resource, weekday=BusinessHours.Weekday.SUNDAY)
    monday = BusinessHours.objects.get(resource=resource, weekday=BusinessHours.Weekday.MONDAY)

    assert sunday.is_closed is True
    assert monday.opens_at == time(7, 0)
    assert monday.closes_at == time(19, 0)


@pytest.mark.django_db
def test_booking_policy_defaults_are_abuse_aware():
    policy = BookingPolicy.objects.create()

    assert policy.slot_interval_minutes == 30
    assert policy.default_hold_minutes == 10
    assert policy.abuse_hold_minutes == 3
    assert policy.max_daily_bookings == 8
