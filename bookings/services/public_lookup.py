from bookings.models import Booking
from bookings.privacy import hmac_phone_hash


class BookingLookupError(Exception):
    pass


def public_booking_summary(public_id, phone):
    phone_hash = hmac_phone_hash(phone)
    booking = (
        Booking.objects.select_related("customer_profile", "service", "resource")
        .filter(public_id=public_id, customer_profile__phone_hash_hmac=phone_hash)
        .first()
    )
    if booking is None:
        raise BookingLookupError("Booking not found.")
    return {
        "public_id": str(booking.public_id),
        "status": booking.status,
        "service": booking.service.name,
        "starts_at": booking.starts_at.isoformat(),
    }
