from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from bookings.services.policy import validate_booking_window
from bookings.tests.factories import create_service_resource_customer


@pytest.mark.django_db
def test_naive_datetimes_are_rejected():
    service, resource, customer = create_service_resource_customer()

    with pytest.raises(ValidationError):
        validate_booking_window(
            starts_at=datetime(2026, 7, 1, 9, 0),
            ends_at=datetime(2026, 7, 1, 10, 0),
            service=service,
            resource=resource,
            customer_profile=customer,
        )


@pytest.mark.django_db
def test_nairobi_boundary_converts_to_utc_and_enforces_hours():
    service, resource, customer = create_service_resource_customer()
    nairobi = ZoneInfo("Africa/Nairobi")
    starts = datetime(2026, 7, 1, 9, 0, tzinfo=nairobi)
    ends = starts + timedelta(minutes=service.duration_minutes)

    normalized_start, normalized_end = validate_booking_window(
        starts_at=starts,
        ends_at=ends,
        service=service,
        resource=resource,
        customer_profile=customer,
    )

    assert normalized_start.utcoffset().total_seconds() == 0
    assert normalized_start.hour == 6
    assert normalized_end.utcoffset().total_seconds() == 0


@pytest.mark.django_db
def test_sunday_normal_booking_and_after_hours_are_rejected():
    service, resource, customer = create_service_resource_customer()
    nairobi = ZoneInfo("Africa/Nairobi")

    sunday = datetime(2026, 7, 5, 9, 0, tzinfo=nairobi)
    with pytest.raises(ValidationError):
        validate_booking_window(
            starts_at=sunday,
            ends_at=sunday + timedelta(minutes=60),
            service=service,
            resource=resource,
            customer_profile=customer,
        )

    late = datetime(2026, 7, 1, 20, 0, tzinfo=nairobi)
    with pytest.raises(ValidationError):
        validate_booking_window(
            starts_at=late,
            ends_at=late + timedelta(minutes=60),
            service=service,
            resource=resource,
            customer_profile=customer,
        )
