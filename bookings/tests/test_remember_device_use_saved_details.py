import pytest

from bookings.models import Booking, CustomerProfile
from bookings.services.remember_device import create_hold_from_remembered_device
from bookings.tests.factories import create_service_resource_customer
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device
from bookings.tests.time_helpers import valid_business_start_utc


@pytest.mark.django_db
def test_remembered_device_can_reuse_saved_details_for_normal_booking_without_exposing_pii(client):
    booking = confirmed_booking(key="remember-use-existing")
    token = remember_device(client, booking)
    service, resource, _customer = create_service_resource_customer()

    result = create_hold_from_remembered_device(
        token=token,
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=valid_business_start_utc(days_ahead=3),
        idempotency_key="remember-use-new-hold",
    )

    repeat_booking = Booking.objects.get(public_id=result["booking_public_id"])
    assert repeat_booking.customer_profile_id == booking.customer_profile_id
    assert CustomerProfile.objects.count() >= 1
    assert "grace@example.com" not in str(result).lower()
    assert "+254" not in str(result)
