import logging
from datetime import time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.models import BOOKING_BLOCKING_STATUSES, Booking, BookingDayPolicy, BookingDayState

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


def default_policy_for_date(local_date):
    weekday = local_date.weekday()
    stored = BookingDayPolicy.objects.filter(weekday=weekday, is_active=True).first()
    if stored:
        return stored
    return built_in_policy_for_weekday(weekday)


def local_date_for_start(starts_at):
    if starts_at is None or timezone.is_naive(starts_at):
        raise ValidationError(GENERIC_POLICY_ERROR)
    return starts_at.astimezone(BUSINESS_TZ).date()


def validate_day_policy_for_selection(*, selection_type, starts_at, package=None, now=None, duration_minutes=0):
    local_start = starts_at.astimezone(BUSINESS_TZ)
    policy = default_policy_for_date(local_start.date())
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


def _active_count(local_date, resource):
    queryset = Booking.objects.filter(
        local_booking_date=local_date,
        resource=resource,
        status__in=BOOKING_BLOCKING_STATUSES,
    )
    now = timezone.now()
    return queryset.exclude(status=Booking.Status.HELD, hold_expires_at__lte=now).count()


def lock_and_validate_day_capacity(*, starts_at, resource, selection_type, package=None, duration_minutes=0):
    local_date = local_date_for_start(starts_at)
    policy = validate_day_policy_for_selection(
        selection_type=selection_type,
        starts_at=starts_at,
        package=package,
        duration_minutes=duration_minutes,
    )
    with transaction.atomic():
        state, _created = BookingDayState.objects.select_for_update().get_or_create(
            local_date=local_date,
            defaults={
                "policy_snapshot_type": policy.day_type,
                "max_clients_snapshot": policy.max_clients,
                "status": BookingDayState.Status.OPEN,
            },
        )
        state = BookingDayState.objects.select_for_update().get(pk=state.pk)
        count = _active_count(local_date, resource)
        if count >= policy.max_clients:
            state.active_client_count_snapshot = count
            state.max_clients_snapshot = policy.max_clients
            state.policy_snapshot_type = policy.day_type
            state.status = BookingDayState.Status.FULL
            state.save(
                update_fields=[
                    "active_client_count_snapshot",
                    "max_clients_snapshot",
                    "policy_snapshot_type",
                    "status",
                    "updated_at",
                ]
            )
            raise ValidationError("Availability unavailable.")
        state.active_client_count_snapshot = count + 1
        state.max_clients_snapshot = policy.max_clients
        state.policy_snapshot_type = policy.day_type
        state.status = BookingDayState.Status.FULL if count + 1 >= policy.max_clients else BookingDayState.Status.OPEN
        state.save(
            update_fields=[
                "active_client_count_snapshot",
                "max_clients_snapshot",
                "policy_snapshot_type",
                "status",
                "updated_at",
            ]
        )
        return state, policy
