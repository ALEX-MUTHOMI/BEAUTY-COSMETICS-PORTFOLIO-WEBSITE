from __future__ import annotations

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.domain.calendar import (
    CALENDAR_TIMEZONE,
    MAX_CALENDAR_RANGE_DAYS,
    classify_calendar_day,
)
from bookings.models import BOOKING_BLOCKING_STATUSES, Booking, BookingDayPolicy
from bookings.services.availability import AvailabilityService, _as_local_date
from bookings.services.bundles import get_full_package_summary, safe_public_text, validate_service_bundle
from bookings.domain.day_policy import BUSINESS_TZ
from bookings.services.day_policy import default_policy_for_date

GENERIC_CALENDAR_ERROR = "Calendar unavailable."


def _count_blocking_clients(local_date: date) -> int:
    now = timezone.now()
    queryset = Booking.objects.filter(
        local_booking_date=local_date,
        status__in=BOOKING_BLOCKING_STATUSES,
    )
    return queryset.exclude(status=Booking.Status.HELD, hold_expires_at__lte=now).count()


def _today_nairobi() -> date:
    return timezone.now().astimezone(BUSINESS_TZ).date()


def _validate_range(start_date, end_date) -> tuple[date, date]:
    if start_date:
        start_day = _as_local_date(start_date)
    else:
        start_day = _today_nairobi()
    if end_date:
        end_day = _as_local_date(end_date)
    else:
        end_day = start_day + timedelta(days=MAX_CALENDAR_RANGE_DAYS - 1)
    if end_day < start_day:
        raise ValidationError(GENERIC_CALENDAR_ERROR)
    range_days = (end_day - start_day).days + 1
    if range_days > MAX_CALENDAR_RANGE_DAYS:
        raise ValidationError(GENERIC_CALENDAR_ERROR)
    return start_day, end_day


def _policy_payload(policy: BookingDayPolicy) -> dict:
    return {
        "day_type": policy.day_type,
        "normal_bookings_allowed": policy.normal_bookings_allowed,
        "full_package_allowed": policy.full_package_allowed,
        "max_clients": 0 if policy.day_type == BookingDayPolicy.DayType.CLOSED else policy.max_clients,
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
        normalized_type = str(selection_type or "normal").strip().lower()
        start_day, end_day = _validate_range(start_date, end_date)

        if normalized_type == "full_package":
            summary = get_full_package_summary(full_package_public_id)
            availability = AvailabilityService.get_full_package_available_slots(
                full_package_public_id,
                start_day,
                end_day,
                resource_id=resource_id,
                request_context=request_context,
            )
            selection = {
                "type": "full_package",
                "public_id": str(summary.full_package.public_id),
                "name": safe_public_text(summary.full_package.name),
                "slug": summary.full_package.slug,
            }
        elif normalized_type == "normal":
            summary = validate_service_bundle([service_public_id])
            availability = AvailabilityService.get_available_slots(
                service_public_id,
                start_day,
                end_day,
                resource_id=resource_id,
                request_context=request_context,
            )
            service = summary.items[0].service
            selection = {
                "type": "normal",
                "public_id": str(service.id),
                "name": safe_public_text(service.name),
                "slug": service.slug,
            }
        else:
            raise ValidationError(GENERIC_CALENDAR_ERROR)

        slots_by_date = {row["date"]: row["slots"] for row in availability}
        days = []
        for offset in range((end_day - start_day).days + 1):
            current = start_day + timedelta(days=offset)
            policy = default_policy_for_date(current)
            policy_data = _policy_payload(policy)
            booked = _count_blocking_clients(current)
            slot_count = len(slots_by_date.get(current.isoformat(), []))
            classified = classify_calendar_day(
                selection_type=normalized_type,
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

        return {
            "timezone": CALENDAR_TIMEZONE,
            "range": {"start": start_day.isoformat(), "end": end_day.isoformat()},
            "selection": selection,
            "days": days,
        }
