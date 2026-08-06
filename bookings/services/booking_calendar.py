from __future__ import annotations

import logging
import time
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils import timezone

from bookings.domain.calendar import (
    CALENDAR_LAYOUT,
    CALENDAR_OFFERED_DAYS_COUNT,
    CALENDAR_SCAN_HORIZON_DAYS,
    CALENDAR_TIMEZONE,
    MAX_CALENDAR_RANGE_DAYS,
    classify_calendar_day,
    group_days_into_weeks,
    iter_offered_dates,
)
from bookings.domain.calendar_policy import CalendarPolicy
from bookings.domain.day_policy import BUSINESS_TZ
from bookings.domain.selection import BookableSelection
from bookings.models import BOOKING_BLOCKING_STATUSES, Booking
from bookings.services.availability import MAX_AVAILABILITY_RANGE_DAYS, AvailabilityService, _as_local_date
from bookings.services.calendar_cache import CalendarCache
from bookings.services.calendar_selection import GENERIC_CALENDAR_ERROR, resolve_calendar_selection
from bookings.services.query_observability import count_db_queries
from bookings.services.service_day_rules import offered_weekdays_for_selection

logger = logging.getLogger("bookings.calendar")


def _partition_dates_for_availability(
    dates: list[date], *, max_span_days: int = MAX_AVAILABILITY_RANGE_DAYS
) -> list[list[date]]:
    """Batch dates so each availability call spans at most *max_span_days*."""
    if not dates:
        return []
    ordered = sorted(dates)
    batches: list[list[date]] = []
    current = [ordered[0]]
    for day in ordered[1:]:
        if (day - current[0]).days + 1 <= max_span_days:
            current.append(day)
        else:
            batches.append(current)
            current = [day]
    batches.append(current)
    return batches


def _count_blocking_clients_bulk(dates: list[date]) -> dict[date, int]:
    if not dates:
        return {}
    now = timezone.now()
    rows = (
        Booking.objects.filter(
            local_booking_date__in=dates,
            status__in=BOOKING_BLOCKING_STATUSES,
        )
        .exclude(status=Booking.Status.HELD, hold_expires_at__lte=now)
        .values("local_booking_date")
        .annotate(booked=Count("id"))
    )
    return {row["local_booking_date"]: row["booked"] for row in rows}


def _today_nairobi() -> date:
    return timezone.now().astimezone(BUSINESS_TZ).date()


def _validate_range(start_date, end_date) -> tuple[date, date]:
    explicit_range = bool(start_date or end_date)
    if start_date:
        start_day = _as_local_date(start_date)
    else:
        start_day = _today_nairobi()
    if end_date:
        end_day = _as_local_date(end_date)
    elif start_date:
        end_day = start_day + timedelta(days=MAX_CALENDAR_RANGE_DAYS - 1)
    else:
        end_day = start_day + timedelta(days=CALENDAR_SCAN_HORIZON_DAYS - 1)
    if end_day < start_day:
        raise ValidationError(GENERIC_CALENDAR_ERROR)
    if explicit_range:
        range_days = (end_day - start_day).days + 1
        if range_days > MAX_CALENDAR_RANGE_DAYS:
            raise ValidationError(GENERIC_CALENDAR_ERROR)
    return start_day, end_day


def _offered_dates_for_window(selection: BookableSelection, start_day: date, end_day: date) -> list[date]:
    scan_start = max(start_day, _today_nairobi())
    horizon_end = min(end_day, scan_start + timedelta(days=CALENDAR_SCAN_HORIZON_DAYS - 1))
    return iter_offered_dates(
        selection.selection_type,
        start=scan_start,
        horizon_end=horizon_end,
        count=CALENDAR_OFFERED_DAYS_COUNT,
        policy_profile=selection.policy_profile,
        offered_weekdays=offered_weekdays_for_selection(selection),
    )


def _slots_by_date(
    *,
    selection: BookableSelection,
    slot_start: date,
    slot_end: date,
    resource_id,
    request_context,
) -> dict[str, list]:
    if slot_end < slot_start:
        return {}
    try:
        if selection.selection_type == "full_package":
            availability = AvailabilityService.get_full_package_available_slots(
                str(selection.public_id),
                slot_start,
                slot_end,
                resource_id=resource_id,
                request_context=request_context,
            )
        else:
            availability = AvailabilityService.get_available_slots(
                str(selection.public_id),
                slot_start,
                slot_end,
                resource_id=resource_id,
                request_context=request_context,
            )
    except ValidationError:
        # Policy/validation: treat as no slots for this window.
        return {}
    except Exception:
        logger.exception(
            "booking.calendar.slots_fetch_failed",
            extra={
                "selection_id": str(selection.public_id),
                "slot_start": slot_start.isoformat(),
                "slot_end": slot_end.isoformat(),
            },
        )
        # Fail closed: do not classify days as empty/full when infra failed.
        raise
    return {row["date"]: row["slots"] for row in availability}


def _slots_for_dates(
    *,
    selection: BookableSelection,
    dates: list[date],
    resource_id,
    request_context,
) -> dict[str, list]:
    """Fetch slots for many days with O(batches) availability calls, not O(days)."""
    wanted = {day.isoformat() for day in dates}
    slots_by_date: dict[str, list] = {}
    for batch in _partition_dates_for_availability(dates):
        fetched = _slots_by_date(
            selection=selection,
            slot_start=batch[0],
            slot_end=batch[-1],
            resource_id=resource_id,
            request_context=request_context,
        )
        for key, slots in fetched.items():
            if key in wanted:
                slots_by_date[key] = slots
    return slots_by_date


def _selection_api_payload(selection: BookableSelection) -> dict:
    return {
        "type": selection.selection_type,
        "public_id": str(selection.public_id),
        "name": selection.name,
        "slug": selection.slug,
    }


class BookingCalendarService:
    @classmethod
    def build_calendar(
        cls,
        *,
        selection_type: str,
        service_public_id=None,
        full_package_public_id=None,
        start_date=None,
        end_date=None,
        resource_id=None,
        request_context=None,
    ) -> dict:
        selection = resolve_calendar_selection(
            selection_type=selection_type,
            service_public_id=service_public_id,
            full_package_public_id=full_package_public_id,
        )
        return cls.build_calendar_for_selection(
            selection=selection,
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
            request_context=request_context,
        )

    @classmethod
    def build_calendar_for_selection(
        cls,
        *,
        selection: BookableSelection,
        start_date,
        end_date,
        resource_id=None,
        request_context=None,
    ) -> dict:
        started = time.perf_counter()
        request_context = request_context or {}
        redis_client = request_context.get("redis_client")

        start_day, end_day = _validate_range(start_date, end_date)
        offered_dates = _offered_dates_for_window(selection, start_day, end_day)
        if not offered_dates:
            raise ValidationError(GENERIC_CALENDAR_ERROR)

        cache_key = CalendarCache.build_key(
            selection_public_id=selection.public_id,
            offered_dates=offered_dates,
            resource_id=resource_id,
            redis_client=redis_client,
        )
        cached = CalendarCache.get_payload(cache_key, redis_client=redis_client)
        if cached is not None:
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "calendar.build",
                extra={
                    "slug": selection.slug,
                    "days_count": len(cached.get("days", [])),
                    "status_histogram": CalendarCache.status_histogram(cached.get("days", [])),
                    "duration_ms": duration_ms,
                    "query_count": 0,
                    "cache_hit": True,
                    "availability_batches": 0,
                },
            )
            return cached

        # DB work: bulk capacity, then batched slot fetches (never O(days) RTT).
        with count_db_queries() as queries:
            try:
                booked_by_date = _count_blocking_clients_bulk(offered_dates)
            except Exception:
                raise ValidationError(GENERIC_CALENDAR_ERROR) from None

            # Only non-full offered days need slot detail for classification.
            dates_needing_slots: list[date] = []
            policy_by_date: dict[date, dict] = {}
            for current in offered_dates:
                day_policy = CalendarPolicy.for_date(selection=selection, local_date=current)
                if not day_policy.offered:
                    continue
                policy_data = day_policy.classification_payload()
                policy_by_date[current] = policy_data
                booked = booked_by_date.get(current, 0)
                if booked < policy_data["max_clients"] and policy_data["max_clients"] > 0:
                    dates_needing_slots.append(current)

            availability_batches = len(_partition_dates_for_availability(dates_needing_slots))
            slots_by_date = _slots_for_dates(
                selection=selection,
                dates=dates_needing_slots,
                resource_id=resource_id,
                request_context=request_context,
            )

            days = []
            for current in offered_dates:
                maybe_policy = policy_by_date.get(current)
                if maybe_policy is None:
                    continue
                policy_data = maybe_policy
                booked = booked_by_date.get(current, 0)
                slot_count = len(slots_by_date.get(current.isoformat(), []))
                classified = classify_calendar_day(
                    selection_type=selection.selection_type,
                    day_type=policy_data["day_type"],
                    normal_bookings_allowed=policy_data["normal_bookings_allowed"],
                    full_package_allowed=policy_data["full_package_allowed"],
                    max_clients=policy_data["max_clients"],
                    booked_clients=booked,
                    slot_count=slot_count,
                )
                days.append(
                    {
                        "date": current.isoformat(),
                        "weekday": current.weekday(),
                        "day_type": policy_data["day_type"],
                        **classified,
                    }
                )

            if not days:
                raise ValidationError(GENERIC_CALENDAR_ERROR)

            range_start = days[0]["date"]
            range_end = days[-1]["date"]
            payload = {
                "timezone": CALENDAR_TIMEZONE,
                "layout": CALENDAR_LAYOUT.get(selection.calendar_layout_key, "singles"),
                "range": {"start": range_start, "end": range_end},
                "selection": _selection_api_payload(selection),
                "days": days,
                "weeks": group_days_into_weeks(days),
            }
            CalendarCache.set_payload(cache_key, payload, redis_client=redis_client)
            query_count = queries["n"]

        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "calendar.build",
            extra={
                "slug": selection.slug,
                "days_count": len(days),
                "status_histogram": CalendarCache.status_histogram(days),
                "duration_ms": duration_ms,
                "query_count": query_count,
                "cache_hit": False,
                "availability_batches": availability_batches,
            },
        )
        return payload
