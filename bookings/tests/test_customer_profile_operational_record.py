import pytest

from bookings.models import Booking, CustomerProfile
from bookings.privacy import hmac_email_hash, hmac_phone_hash
from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer
from bookings.tests.time_helpers import valid_business_start_utc


@pytest.mark.django_db
def test_repeat_booking_reuses_customer_profile_by_hmac_without_account_creation(django_user_model):
    service, resource, _customer = create_service_resource_customer()
    payload = {"full_name": "Grace Wanjiku", "email": "grace@example.com", "phone": "+254712345678"}

    first = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=valid_business_start_utc(),
        customer_payload=payload,
        idempotency_key="customer-profile-first",
    )
    second = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=valid_business_start_utc(days_ahead=3),
        customer_payload=payload,
        idempotency_key="customer-profile-second",
    )

    first_booking = Booking.objects.get(public_id=first["booking_public_id"])
    second_booking = Booking.objects.get(public_id=second["booking_public_id"])
    assert first_booking.customer_profile_id == second_booking.customer_profile_id
    assert CustomerProfile.objects.filter(email_hash_hmac=hmac_email_hash(payload["email"])).count() == 1
    assert CustomerProfile.objects.filter(phone_hash_hmac=hmac_phone_hash(payload["phone"])).count() == 1
    assert django_user_model.objects.count() == 0
