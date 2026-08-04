import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.domain.day_policy import (
    BUSINESS_TZ,
    GENERIC_POLICY_ERROR,
    built_in_policy_for_weekday,
    local_date_for_start,
    validate_selection_against_policy,
)
from bookings.models import BOOKING_BLOCKING_STATUSES, Booking, BookingDayPolicy, BookingDayState

logger = logging.getLogger("bookings.day_policy")


def default_policy_for_date(local_date):
    stored = BookingDayPolicy.objects.filter(weekday=local_date.weekday(), is_active=True).first()
    if stored:
        return stored
    return built_in_policy_for_weekday(local_date.weekday())


def validate_day_policy_for_selection(*, selection_type, starts_at, package=None, now=None, duration_minutes=0):
    policy = default_policy_for_date(starts_at.astimezone(BUSINESS_TZ).date())
    return validate_selection_against_policy(
        policy=policy,
        selection_type=selection_type,
        starts_at=starts_at,
        package=package,
        now=now,
        duration_minutes=duration_minutes,
    )


def _active_count(local_date, resource):
    queryset = Booking.objects.filter(
        local_booking_date=local_date,
        resource=resource,
        status__in=BOOKING_BLOCKING_STATUSES,
    )
    now = timezone.now()
    return queryset.exclude(status=Booking.Status.HELD, hold_expires_at__lte=now).count()


def lock_and_validate_day_capacity(
    *,
    starts_at,
    resource,
    selection_type,
    package=None,
    duration_minutes=0,
    yield_duration_minutes=None,
    turnaround_minutes=0,
):
    from bookings.domain.yield_scheduling import resolve_day_client_cap

    local_date = local_date_for_start(starts_at)
    policy = validate_day_policy_for_selection(
        selection_type=selection_type,
        starts_at=starts_at,
        package=package,
        duration_minutes=duration_minutes,
    )
    yield_duration = int(yield_duration_minutes) if yield_duration_minutes is not None else 0
    effective_max = resolve_day_client_cap(
        selection_type=selection_type,
        max_clients_policy=policy.max_clients,
        business_start=policy.business_start_time,
        business_end=policy.business_end_time,
        duration_minutes=yield_duration,
        turnaround_minutes=int(turnaround_minutes or 0),
    )
    with transaction.atomic():
        state, _created = BookingDayState.objects.select_for_update().get_or_create(
            local_date=local_date,
            defaults={
                "policy_snapshot_type": policy.day_type,
                "max_clients_snapshot": effective_max,
                "status": BookingDayState.Status.OPEN,
            },
        )
        state = BookingDayState.objects.select_for_update().get(pk=state.pk)
        count = _active_count(local_date, resource)
        if count >= effective_max:
            state.active_client_count_snapshot = count
            state.max_clients_snapshot = effective_max
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
        state.max_clients_snapshot = effective_max
        state.policy_snapshot_type = policy.day_type
        state.status = BookingDayState.Status.FULL if count + 1 >= effective_max else BookingDayState.Status.OPEN
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


__all__ = [
    "BUSINESS_TZ",
    "GENERIC_POLICY_ERROR",
    "built_in_policy_for_weekday",
    "default_policy_for_date",
    "local_date_for_start",
    "lock_and_validate_day_capacity",
    "validate_day_policy_for_selection",
]
