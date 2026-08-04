from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from bookings.tests.factories import create_booking, create_service_resource_customer


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


@pytest.mark.django_db
def test_attacker_cannot_force_unbounded_availability_scan():
    service, resource, _customer = create_service_resource_customer()

    with pytest.raises(ValidationError):
        _service().get_available_slots(
            service.id,
            timezone.localdate(),
            timezone.localdate() + timedelta(days=365),
            resource_id=resource.id,
        )


@pytest.mark.django_db
def test_unknown_resource_error_is_generic_and_does_not_leak_identifier():
    service, _resource, _customer = create_service_resource_customer()
    unknown = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(ValidationError) as exc:
        _service().get_available_slots(service.id, date(2026, 6, 1), date(2026, 6, 1), resource_id=unknown)

    assert "availability unavailable" in str(exc.value).lower()
    assert unknown not in str(exc.value)


@pytest.mark.django_db
def test_attacker_cannot_see_unavailable_reason_or_conflicting_booking_details():
    service, resource, customer = create_service_resource_customer()
    booking = create_booking(
        service=service,
        resource=resource,
        customer_profile=customer,
        starts_at=timezone.now() + timedelta(days=5),
        ends_at=timezone.now() + timedelta(days=5, hours=1),
        status=Booking.Status.PAYMENT_PENDING,
    )

    result = _service().get_available_slots(
        service.id,
        booking.starts_at.astimezone(timezone.get_current_timezone()).date(),
        booking.starts_at.astimezone(timezone.get_current_timezone()).date(),
        resource_id=resource.id,
    )

    payload = str(result).lower()
    assert "payment_pending" not in payload
    assert str(booking.id) not in payload
    assert "conflict" not in payload
