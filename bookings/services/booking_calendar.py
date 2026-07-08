from __future__ import annotations

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
from bookings.services.availability import AvailabilityService, _as_local_date
from bookings.services.calendar_selection import GENERIC_CALENDAR_ERROR, resolve_calendar_selection


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
    return {row["date"]: row["slots"] for row in availability}


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
        start_date,
        end_date,
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
        start_day, end_day = _validate_range(start_date, end_date)
        offered_dates = _offered_dates_for_window(selection, start_day, end_day)
        if not offered_dates:
            raise ValidationError(GENERIC_CALENDAR_ERROR)

        booked_by_date = _count_blocking_clients_bulk(offered_dates)
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

        slots_by_date: dict[str, list] = {}
        for current in dates_needing_slots:
            slots_by_date.update(
                _slots_by_date(
                    selection=selection,
                    slot_start=current,
                    slot_end=current,
                    resource_id=resource_id,
                    request_context=request_context,
                )
            )

        days = []
        for current in offered_dates:
            policy_data = policy_by_date.get(current)
            if not policy_data:
                continue
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
        return {
            "timezone": CALENDAR_TIMEZONE,
            "layout": CALENDAR_LAYOUT.get(selection.calendar_layout_key, "singles"),
            "range": {"start": range_start, "end": range_end},
            "selection": _selection_api_payload(selection),
            "days": days,
            "weeks": group_days_into_weeks(days),
        }
