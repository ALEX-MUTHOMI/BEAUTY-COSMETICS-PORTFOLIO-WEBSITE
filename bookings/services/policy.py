from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import BusinessHours

NAIROBI = ZoneInfo("Africa/Nairobi")
UTC = ZoneInfo("UTC")


def _require_aware(value, field_name):
    if timezone.is_naive(value):
        raise ValidationError({field_name: "Datetime must be timezone-aware."})


def validate_booking_window(starts_at, ends_at, service, resource, customer_profile):
    _require_aware(starts_at, "starts_at")
    _require_aware(ends_at, "ends_at")
    if starts_at >= ends_at:
        raise ValidationError("Booking starts_at must be before ends_at.")

    local_start = starts_at.astimezone(NAIROBI)
    local_end = ends_at.astimezone(NAIROBI)
    hours = BusinessHours.objects.filter(resource=resource, weekday=local_start.weekday()).first()
    if hours is None:
        raise ValidationError("Business hours are not configured.")
    if hours.is_closed:
        raise ValidationError("Normal bookings are not allowed on closed days.")
    if local_start.time() < hours.opens_at or local_end.time() > hours.closes_at:
        raise ValidationError("Booking is outside business hours.")

    return starts_at.astimezone(UTC), ends_at.astimezone(UTC)
