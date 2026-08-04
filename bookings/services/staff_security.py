from bookings.models import StaffActionAuditEvent
from bookings.privacy import decrypt_value


class PermissionDenied(Exception):
    pass


def _require_staff(user):
    if not getattr(user, "is_staff", False):
        raise PermissionDenied("Staff access required.")


def staff_booking_summary(user, booking):
    _require_staff(user)
    return {
        "public_id": str(booking.public_id),
        "status": booking.status,
        "service": booking.service.name,
        "resource": booking.resource.name,
        "phone": booking.customer_profile.phone_redacted,
        "email": booking.customer_profile.email_redacted,
    }


def reveal_customer_contact(user, booking, reason):
    _require_staff(user)
    StaffActionAuditEvent.objects.create(
        staff=user,
        booking=booking,
        action=StaffActionAuditEvent.Action.CONTACT_REVEAL,
        reason=reason[:255],
        metadata_redacted={"public_id": str(booking.public_id)},
    )
    return {
        "phone": decrypt_value(booking.customer_profile.phone_encrypted),
        "email": decrypt_value(booking.customer_profile.email_encrypted),
    }
