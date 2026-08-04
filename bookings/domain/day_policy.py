import logging
from datetime import time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import BookingDayPolicy

BUSINESS_TZ = ZoneInfo("Africa/Nairobi")
GENERIC_POLICY_ERROR = "Booking selection unavailable."
logger = logging.getLogger("bookings.day_policy")


def built_in_policy_for_weekday(weekday):
    if weekday in {0, 3, 4, 5}:
        return BookingDayPolicy(
            weekday=weekday,
            day_type=BookingDayPolicy.DayType.NORMAL,
            business_start_time=time(7, 0),
            business_end_time=time(19, 0),
            max_clients=5,
            normal_bookings_allowed=True,
            full_package_allowed=False,
        )
    if weekday in {1, 2}:
        return BookingDayPolicy(
            weekday=weekday,
            day_type=BookingDayPolicy.DayType.FULL_PACKAGE,
            business_start_time=time(7, 0),
            business_end_time=time(19, 0),
            max_clients=3,
            full_package_notice_hours=24,
            normal_bookings_allowed=False,
            full_package_allowed=True,
        )
    return BookingDayPolicy(
        weekday=weekday,
        day_type=BookingDayPolicy.DayType.CLOSED,
        business_start_time=time(7, 0),
        business_end_time=time(19, 0),
        max_clients=0,
        normal_bookings_allowed=False,
        full_package_allowed=False,
    )


def local_date_for_start(starts_at):
    if starts_at is None or timezone.is_naive(starts_at):
        raise ValidationError(GENERIC_POLICY_ERROR)
    return starts_at.astimezone(BUSINESS_TZ).date()


def validate_selection_against_policy(
    *,
    policy,
    selection_type,
    starts_at,
    package=None,
    now=None,
    duration_minutes=0,
):
    local_start = starts_at.astimezone(BUSINESS_TZ)
    local_end = local_start + timedelta(minutes=duration_minutes or getattr(package, "duration_minutes", 0))
    business_start = local_start.replace(
        hour=policy.business_start_time.hour,
        minute=policy.business_start_time.minute,
        second=0,
        microsecond=0,
    )
    business_end = local_start.replace(
        hour=policy.business_end_time.hour,
        minute=policy.business_end_time.minute,
        second=0,
        microsecond=0,
    )
    if selection_type == "normal" and not policy.normal_bookings_allowed:
        raise ValidationError(GENERIC_POLICY_ERROR)
    if selection_type == "full_package" and not policy.full_package_allowed:
        raise ValidationError(GENERIC_POLICY_ERROR)
    if policy.day_type == BookingDayPolicy.DayType.CLOSED:
        raise ValidationError(GENERIC_POLICY_ERROR)
    if local_start < business_start or local_end > business_end:
        raise ValidationError(GENERIC_POLICY_ERROR)
    if selection_type == "full_package":
        notice_hours = getattr(package, "notice_required_hours", policy.full_package_notice_hours)
        current = (now or timezone.now()).astimezone(BUSINESS_TZ)
        appointment_day_start = local_start.replace(hour=0, minute=0, second=0, microsecond=0)
        if appointment_day_start - current < timedelta(hours=notice_hours):
            raise ValidationError(GENERIC_POLICY_ERROR)
    return policy
