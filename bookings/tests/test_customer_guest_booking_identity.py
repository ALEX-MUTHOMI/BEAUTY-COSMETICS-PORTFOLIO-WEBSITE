import pytest
from django.contrib.auth import get_user_model

from bookings.privacy import hmac_email_hash, hmac_phone_hash
from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer
from bookings.tests.time_helpers import valid_business_start_utc


@pytest.mark.django_db(transaction=True)
def test_guest_hold_creates_encrypted_hmac_redacted_customer_without_account():
    service, resource, _customer = create_service_resource_customer()
    starts_at = valid_business_start_utc()

    response = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=starts_at,
        customer_payload={
            "full_name": "Grace Wanjiku",
            "email": "Grace.Customer@example.com",
            "phone": "0712345678",
        },
        idempotency_key="guest-identity-b5",
    )

    from bookings.models import Booking

    booking = Booking.objects.get(public_id=response["booking_public_id"])
    profile = booking.customer_profile

    assert get_user_model().objects.filter(email="grace.customer@example.com").count() == 0
    assert "Grace Wanjiku" not in profile.full_name_encrypted
    assert "grace.customer@example.com" not in profile.email_encrypted
    assert "+254712345678" not in profile.phone_encrypted
    assert profile.email_hash_hmac == hmac_email_hash("grace.customer@example.com")
    assert profile.phone_hash_hmac == hmac_phone_hash("+254712345678")
    assert profile.email_redacted == "g***@example.com"
    assert profile.phone_redacted == "+2547***678"
