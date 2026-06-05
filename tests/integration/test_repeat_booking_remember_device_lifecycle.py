import pytest

from bookings.models import Booking
from bookings.services.remember_device import create_hold_from_remembered_device
from bookings.tests.factories import create_service_resource_customer
from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device
from bookings.tests.time_helpers import valid_business_start_utc


@pytest.mark.django_db(transaction=True)
def test_repeat_booking_remember_device_lifecycle_does_not_require_account_or_otp(client, django_user_model):
    booking = confirmed_booking(key="remember-lifecycle")
    token = remember_device(client, booking)
    service, resource, _customer = create_service_resource_customer()

    result = create_hold_from_remembered_device(
        token=token,
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=valid_business_start_utc(days_ahead=4),
        idempotency_key="remember-lifecycle-repeat",
    )

    repeat = Booking.objects.get(public_id=result["booking_public_id"])
    assert repeat.customer_profile_id == booking.customer_profile_id
    assert repeat.status == Booking.Status.HELD
    assert django_user_model.objects.count() == 0
