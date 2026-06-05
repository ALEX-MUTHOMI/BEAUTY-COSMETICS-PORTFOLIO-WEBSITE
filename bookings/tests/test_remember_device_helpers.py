from bookings.models import Booking
from bookings.services.remember_device import issue_returning_device_token
from bookings.tests.test_booking_checkout_contract import _held_booking


def confirmed_booking(key="remember-device-helper"):
    booking = _held_booking(key=key)
    booking.status = Booking.Status.CONFIRMED
    booking.confirmed_at = booking.starts_at
    booking.save(update_fields=["status", "confirmed_at", "updated_at"])
    return booking


def remember_device(client, booking):
    response = client.post(
        "/api/customers/remember-device/",
        {"booking_public_id": str(booking.public_id), "remember_device": True},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 201
    return response.cookies["bc_remember_device"].value


def create_many_devices(customer_profile, count):
    tokens = []
    for index in range(count):
        token, _device = issue_returning_device_token(
            customer_profile=customer_profile,
            ip="203.0.113.10",
            user_agent=f"pytest-{index}",
            enforce_device_limit=False,
        )
        tokens.append(token)
    return tokens
