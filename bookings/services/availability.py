import logging
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from bookings.models import BlackoutPeriod, BookableResource, Booking, BookingPolicy, BusinessHours, Service

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

        circuit_mode = _safe_increment_counter(request_context)
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
        for offset in range(range_days):
            day = start_day + timedelta(days=offset)
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
                        )
                    )
            results.append({"date": day.isoformat(), "timezone": "Africa/Nairobi", "slots": day_slots})

        logger.info(
            "booking.availability.generated",
            extra={
                "service_public_id": str(service.id),
                "resource_public_id": str(resource_id) if resource_id else "all",
                "date_range_days": range_days,
                "result_slot_count": sum(len(day["slots"]) for day in results),
                "circuit_breaker_mode": circuit_mode,
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
    def _slots_for_resource_day(cls, service, resource, day, business_hours, bookings, blackouts, policy):
        opens_at, closes_at = cls._hours_for_day(day, business_hours)
        if not opens_at or not closes_at:
            return []

        business_start = datetime.combine(day, opens_at, tzinfo=BUSINESS_TZ)
        business_end = datetime.combine(day, closes_at, tzinfo=BUSINESS_TZ)
        if cls._capacity_reached(resource, day, bookings, policy):
            return []

        busy = cls._busy_intervals_for_day(resource, day, bookings, blackouts)
        free = subtract_intervals([(business_start, business_end)], busy)
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
    def _hours_for_day(day, business_hours):
        if business_hours:
            if business_hours.is_closed:
                return None, None
            return business_hours.opens_at, business_hours.closes_at
        defaults = _default_business_hours(day)
        if not defaults:
            return None, None
        return defaults

    @staticmethod
    def _capacity_reached(resource, day, bookings, policy):
        count = 0
        for booking in bookings:
            if booking.resource_id != resource.id:
                continue
            if booking.starts_at.astimezone(BUSINESS_TZ).date() == day:
                count += 1
        return count >= policy.max_daily_bookings

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
