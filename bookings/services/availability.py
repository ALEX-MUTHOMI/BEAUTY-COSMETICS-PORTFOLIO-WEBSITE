import logging
from datetime import date, datetime, time, timedelta
from time import perf_counter
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from bookings.domain.day_policy import built_in_policy_for_weekday
from bookings.domain.yield_scheduling import (
    filter_candidates_to_free_intervals,
    generate_duration_stepped_anchors,
    resolve_day_client_cap,
)
from bookings.models import (
    BlackoutPeriod,
    BookableResource,
    Booking,
    BookingDayPolicy,
    BookingPolicy,
    BusinessHours,
    Service,
)
from bookings.services.bundles import get_full_package_summary, validate_service_bundle
from bookings.services.day_policy import default_policy_for_date
from bookings.services.query_observability import count_db_queries

BUSINESS_TZ = ZoneInfo("Africa/Nairobi")
MAX_AVAILABILITY_RANGE_DAYS = 14
AVAILABILITY_COUNTER_KEY = "booking:availability:requests:10m"
AVAILABILITY_COUNTER_TTL_SECONDS = 600
GENERIC_UNAVAILABLE = "Availability unavailable."
logger = logging.getLogger("bookings.availability")


def merge_intervals(intervals):
    """Merge overlapping intervals only; adjacent [a,b) and [b,c) stay distinct."""
    ordered = sorted(intervals, key=lambda item: item[0])
    if not ordered:
        return []
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        current_start, current_end = merged[-1]
        if start < current_end:
            merged[-1] = (current_start, max(current_end, end))
        else:
            merged.append((start, end))
    return merged


def subtract_intervals(windows, busy_intervals):
    free = []
    busy = merge_intervals(busy_intervals)
    for window_start, window_end in windows:
        cursor = window_start
        for busy_start, busy_end in busy:
            if busy_end <= cursor or busy_start >= window_end:
                continue
            if busy_start > cursor:
                free.append((cursor, min(busy_start, window_end)))
            cursor = max(cursor, busy_end)
            if cursor >= window_end:
                break
        if cursor < window_end:
            free.append((cursor, window_end))
    return free


def _align_to_grid(value, slot_interval_minutes):
    minutes = value.hour * 60 + value.minute
    remainder = minutes % slot_interval_minutes
    if remainder:
        value += timedelta(minutes=slot_interval_minutes - remainder)
    return value.replace(second=0, microsecond=0)


def generate_candidates_from_free_intervals(
    free_intervals,
    duration_minutes,
    buffer_before_minutes,
    buffer_after_minutes,
    slot_interval_minutes,
):
    candidates = []
    duration = timedelta(minutes=duration_minutes)
    before = timedelta(minutes=buffer_before_minutes)
    after = timedelta(minutes=buffer_after_minutes)
    interval = timedelta(minutes=slot_interval_minutes)

    for free_start, free_end in free_intervals:
        candidate_start = _align_to_grid(free_start + before, slot_interval_minutes)
        while True:
            service_window_start = candidate_start - before
            actual_end = candidate_start + duration
            service_window_end = actual_end + after
            if service_window_end > free_end:
                break
            if service_window_start >= free_start:
                candidates.append((candidate_start, actual_end))
            candidate_start += interval
    return candidates


def _as_local_date(value):
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError("Date range is invalid.") from exc
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            raise ValidationError("Datetime must be timezone-aware.")
        return value.astimezone(BUSINESS_TZ).date()
    if isinstance(value, date):
        return value
    raise ValidationError("Date range is invalid.")


def _local_day_bounds(day):
    start = datetime.combine(day, time.min, tzinfo=BUSINESS_TZ)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=BUSINESS_TZ)
    return start, end


def _default_business_hours(day):
    if day.weekday() == BusinessHours.Weekday.SUNDAY:
        return None
    return time(7, 0), time(19, 0)


def _is_blocking_booking(booking, now):
    if booking.status == Booking.Status.HELD:
        return bool(booking.hold_expires_at and booking.hold_expires_at > now)
    if booking.status == Booking.Status.RESCHEDULE_HELD:
        return not booking.hold_expires_at or booking.hold_expires_at > now
    return booking.status in {
        Booking.Status.PAYMENT_PENDING,
        Booking.Status.CONFIRMED,
        Booking.Status.CHECKED_IN,
        Booking.Status.LATE,
        Booking.Status.IN_PROGRESS,
    }


def _safe_increment_counter(request_context):
    if not request_context:
        return "normal"
    redis_client = request_context.get("redis_client")
    if not redis_client:
        return "normal"
    try:
        redis_client.incr(AVAILABILITY_COUNTER_KEY)
        redis_client.expire(AVAILABILITY_COUNTER_KEY, AVAILABILITY_COUNTER_TTL_SECONDS)
    except Exception:
        logger.info(
            "booking.availability.degraded",
            extra={"request_id": request_context.get("request_id"), "reason": "redis_unavailable"},
        )
        return "degraded"
    return "normal"


class AvailabilityService:
    @classmethod
    def get_bundle_available_slots(
        cls,
        service_public_ids,
        start_date,
        end_date,
        resource_id=None,
        timezone="Africa/Nairobi",
        request_context=None,
    ):
        summary = validate_service_bundle(service_public_ids)
        return cls._get_selection_available_slots(
            summary=summary,
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
            timezone=timezone,
            request_context=request_context,
        )

    @classmethod
    def get_full_package_available_slots(
        cls,
        full_package_public_id,
        start_date,
        end_date,
        resource_id=None,
        timezone="Africa/Nairobi",
        request_context=None,
    ):
        summary = get_full_package_summary(full_package_public_id)
        return cls._get_selection_available_slots(
            summary=summary,
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
            timezone=timezone,
            request_context=request_context,
        )

    @classmethod
    def _get_selection_available_slots(
        cls,
        *,
        summary,
        start_date,
        end_date,
        resource_id=None,
        timezone="Africa/Nairobi",
        request_context=None,
    ):
        if timezone != "Africa/Nairobi":
            raise ValidationError("Availability unavailable.")
        start_day = _as_local_date(start_date)
        end_day = _as_local_date(end_date)
        if end_day < start_day:
            raise ValidationError("Date range is invalid.")
        range_days = (end_day - start_day).days + 1
        if range_days > MAX_AVAILABILITY_RANGE_DAYS:
            raise ValidationError("Date range is too large.")
        started = perf_counter()
        circuit_mode = _safe_increment_counter(request_context)
        with count_db_queries() as queries:
            resources = cls._get_resources(resource_id)
            policy = BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()
            query_start_local, _ = _local_day_bounds(start_day)
            _, query_end_local = _local_day_bounds(end_day)
            query_start_utc = query_start_local.astimezone(ZoneInfo("UTC"))
            query_end_utc = query_end_local.astimezone(ZoneInfo("UTC"))
            resource_ids = [resource.id for resource in resources]
            business_hours = cls._business_hours_by_resource(resource_ids)
            bookings = cls._blocking_bookings(resource_ids, query_start_utc, query_end_utc)
            blackouts = cls._blackouts(resource_ids, query_start_utc, query_end_utc)
            day_policies = {row.weekday: row for row in BookingDayPolicy.objects.filter(is_active=True)}
            service_like = type(
                "SelectionService",
                (),
                {
                    "id": summary.full_package.public_id if summary.full_package else summary.items[0].service.id,
                    "duration_minutes": summary.total_duration_minutes,
                    "buffer_before_minutes": summary.buffer_before_minutes,
                    "buffer_after_minutes": summary.buffer_after_minutes,
                },
            )()
            results = []
            for offset in range(range_days):
                day = start_day + timedelta(days=offset)
                day_policy = day_policies.get(day.weekday()) or built_in_policy_for_weekday(day.weekday())
                allowed = (
                    summary.selection_type == "normal"
                    and day_policy.normal_bookings_allowed
                    or summary.selection_type == "full_package"
                    and day_policy.full_package_allowed
                )
                day_slots = []
                if allowed:
                    for resource in resources:
                        day_slots.extend(
                            cls._slots_for_resource_day(
                                service_like,
                                resource,
                                day,
                                business_hours.get((resource.id, day.weekday())),
                                bookings,
                                blackouts,
                                policy,
                                selection_type=summary.selection_type,
                                day_policy=day_policy,
                            )
                        )
                results.append({"date": day.isoformat(), "timezone": "Africa/Nairobi", "slots": day_slots})
            query_count = queries["n"]
        logger.info(
            "booking.availability.selection_generated",
            extra={
                "selection_type": summary.selection_type,
                "date_range_days": range_days,
                "result_slot_count": sum(len(day["slots"]) for day in results),
                "circuit_breaker_mode": circuit_mode,
                "duration_ms": int((perf_counter() - started) * 1000),
                "query_count": query_count,
            },
        )
        return results

    @classmethod
    def get_available_slots(
        cls,
        service_id,
        start_date,
        end_date,
        resource_id=None,
        booking_type="normal",
        timezone="Africa/Nairobi",
        request_context=None,
    ):
        if timezone != "Africa/Nairobi":
            raise ValidationError("Availability unavailable.")

        start_day = _as_local_date(start_date)
        end_day = _as_local_date(end_date)
        if end_day < start_day:
            raise ValidationError("Date range is invalid.")
        range_days = (end_day - start_day).days + 1
        if range_days > MAX_AVAILABILITY_RANGE_DAYS:
            raise ValidationError("Date range is too large.")

        started = perf_counter()
        circuit_mode = _safe_increment_counter(request_context)
        with count_db_queries() as queries:
            service = cls._get_service(service_id)
            resources = cls._get_resources(resource_id)
            policy = BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()

            query_start_local, _ = _local_day_bounds(start_day)
            _, query_end_local = _local_day_bounds(end_day)
            query_start_utc = query_start_local.astimezone(ZoneInfo("UTC"))
            query_end_utc = query_end_local.astimezone(ZoneInfo("UTC"))

            resource_ids = [resource.id for resource in resources]
            business_hours = cls._business_hours_by_resource(resource_ids)
            bookings = cls._blocking_bookings(resource_ids, query_start_utc, query_end_utc)
            blackouts = cls._blackouts(resource_ids, query_start_utc, query_end_utc)

            results = []
            day_policies = {row.weekday: row for row in BookingDayPolicy.objects.filter(is_active=True)}
            for offset in range(range_days):
                day = start_day + timedelta(days=offset)
                day_policy = day_policies.get(day.weekday()) or built_in_policy_for_weekday(day.weekday())
                day_slots = []
                if not (booking_type == "normal" and day.weekday() == BusinessHours.Weekday.SUNDAY):
                    for resource in resources:
                        day_slots.extend(
                            cls._slots_for_resource_day(
                                service,
                                resource,
                                day,
                                business_hours.get((resource.id, day.weekday())),
                                bookings,
                                blackouts,
                                policy,
                                selection_type="normal" if booking_type == "normal" else booking_type,
                                day_policy=day_policy,
                            )
                        )
                results.append({"date": day.isoformat(), "timezone": "Africa/Nairobi", "slots": day_slots})
            query_count = queries["n"]

        logger.info(
            "booking.availability.generated",
            extra={
                "service_public_id": str(service.id),
                "resource_public_id": str(resource_id) if resource_id else "all",
                "date_range_days": range_days,
                "result_slot_count": sum(len(day["slots"]) for day in results),
                "circuit_breaker_mode": circuit_mode,
                "duration_ms": int((perf_counter() - started) * 1000),
                "query_count": query_count,
            },
        )
        return results

    @staticmethod
    def _get_service(service_id):
        try:
            service = Service.objects.filter(id=service_id, is_active=True).first()
        except (TypeError, ValueError):
            service = None
        if not service:
            raise ValidationError(GENERIC_UNAVAILABLE)
        return service

    @staticmethod
    def _get_resources(resource_id):
        try:
            queryset = BookableResource.objects.filter(is_active=True)
            if resource_id:
                queryset = queryset.filter(id=resource_id)
            resources = list(queryset)
        except (TypeError, ValueError):
            resources = []
        if not resources:
            raise ValidationError(GENERIC_UNAVAILABLE)
        return resources

    @staticmethod
    def _business_hours_by_resource(resource_ids):
        rows = BusinessHours.objects.filter(resource_id__in=resource_ids)
        return {(row.resource_id, row.weekday): row for row in rows}

    @staticmethod
    def _blocking_bookings(resource_ids, query_start_utc, query_end_utc):
        candidates = Booking.objects.filter(
            resource_id__in=resource_ids,
            starts_at__lt=query_end_utc,
            ends_at__gt=query_start_utc,
        ).filter(
            Q(
                status__in=[
                    Booking.Status.HELD,
                    Booking.Status.PAYMENT_PENDING,
                    Booking.Status.CONFIRMED,
                    Booking.Status.RESCHEDULE_HELD,
                    Booking.Status.CHECKED_IN,
                    Booking.Status.LATE,
                    Booking.Status.IN_PROGRESS,
                ]
            )
        )
        now = timezone.now()
        return [booking for booking in candidates if _is_blocking_booking(booking, now)]

    @staticmethod
    def _blackouts(resource_ids, query_start_utc, query_end_utc):
        return list(
            BlackoutPeriod.objects.filter(
                Q(resource_id__in=resource_ids) | Q(resource__isnull=True),
                starts_at__lt=query_end_utc,
                ends_at__gt=query_start_utc,
            )
        )

    @classmethod
    def _slots_for_resource_day(
        cls,
        service,
        resource,
        day,
        business_hours,
        bookings,
        blackouts,
        policy,
        *,
        selection_type="normal",
        day_policy=None,
    ):
        day_policy = day_policy or default_policy_for_date(day)
        opens_at, closes_at = cls._hours_for_day(day, business_hours, day_policy=day_policy)
        if not opens_at or not closes_at:
            return []

        business_start = datetime.combine(day, opens_at, tzinfo=BUSINESS_TZ)
        business_end = datetime.combine(day, closes_at, tzinfo=BUSINESS_TZ)
        turnaround = int(getattr(service, "buffer_before_minutes", 0) or 0) + int(
            getattr(service, "buffer_after_minutes", 0) or 0
        )
        max_clients = resolve_day_client_cap(
            selection_type=selection_type,
            max_clients_policy=day_policy.max_clients,
            business_start=opens_at,
            business_end=closes_at,
            duration_minutes=int(getattr(service, "duration_minutes", 0) or 0),
            turnaround_minutes=turnaround,
        )
        if cls._capacity_reached(resource, day, bookings, max_clients):
            return []

        busy = cls._busy_intervals_for_day(resource, day, bookings, blackouts)
        free = subtract_intervals([(business_start, business_end)], busy)

        if selection_type == "full_package":
            anchors = generate_duration_stepped_anchors(
                business_start,
                business_end,
                service.duration_minutes,
                service.buffer_before_minutes,
                service.buffer_after_minutes,
                max_clients,
            )
            candidates = filter_candidates_to_free_intervals(
                anchors,
                free,
                service.buffer_before_minutes,
                service.buffer_after_minutes,
            )
        else:
            candidates = generate_candidates_from_free_intervals(
                free,
                service.duration_minutes,
                service.buffer_before_minutes,
                service.buffer_after_minutes,
                policy.slot_interval_minutes,
            )
        return [
            {
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
                "duration_minutes": service.duration_minutes,
                "buffer_minutes": service.buffer_before_minutes + service.buffer_after_minutes,
                "resource_public_id": str(resource.id),
                "service_public_id": str(service.id),
            }
            for starts_at, ends_at in candidates
        ]

    @staticmethod
    def _hours_for_day(day, business_hours, day_policy=None):
        # Prefer BookingDayPolicy hours so availability matches hold validation.
        if day_policy is not None:
            if day_policy.day_type == BookingDayPolicy.DayType.CLOSED or day_policy.max_clients <= 0:
                return None, None
            return day_policy.business_start_time, day_policy.business_end_time
        if business_hours:
            if business_hours.is_closed:
                return None, None
            return business_hours.opens_at, business_hours.closes_at
        defaults = _default_business_hours(day)
        if not defaults:
            return None, None
        return defaults

    @staticmethod
    def _capacity_reached(resource, day, bookings, max_clients):
        if max_clients <= 0:
            return True
        count = 0
        for booking in bookings:
            if booking.resource_id != resource.id:
                continue
            if booking.starts_at.astimezone(BUSINESS_TZ).date() == day:
                count += 1
        return count >= max_clients

    @staticmethod
    def _busy_intervals_for_day(resource, day, bookings, blackouts):
        day_start, day_end = _local_day_bounds(day)
        intervals = []
        for booking in bookings:
            if booking.resource_id != resource.id:
                continue
            start = booking.starts_at.astimezone(BUSINESS_TZ)
            end = booking.ends_at.astimezone(BUSINESS_TZ)
            if start < day_end and end > day_start:
                intervals.append((max(start, day_start), min(end, day_end)))
        for blackout in blackouts:
            if blackout.resource_id and blackout.resource_id != resource.id:
                continue
            start = blackout.starts_at.astimezone(BUSINESS_TZ)
            end = blackout.ends_at.astimezone(BUSINESS_TZ)
            if start < day_end and end > day_start:
                intervals.append((max(start, day_start), min(end, day_end)))
        return merge_intervals(intervals)
