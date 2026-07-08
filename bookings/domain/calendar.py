"""Deterministic public booking calendar — domain constants and classification."""

from __future__ import annotations

from datetime import date, timedelta

MAX_CALENDAR_RANGE_DAYS = 42
CALENDAR_TIMEZONE = "Africa/Nairobi"
CALENDAR_OFFERED_DAYS_COUNT = 8
CALENDAR_SCAN_HORIZON_DAYS = 126

# Monday=0 … Sunday=6 — must match bookings.services.day_policy defaults.
OFFERED_WEEKDAYS: dict[str, frozenset[int]] = {
    "normal": frozenset({0, 3, 4, 5}),
    "full_package": frozenset({1, 2}),
}

OFFERED_WEEKDAYS_BY_PROFILE: dict[str, frozenset[int]] = {
    "single": OFFERED_WEEKDAYS["normal"],
    "full_package": OFFERED_WEEKDAYS["full_package"],
}


def weekdays_for_policy_profile(policy_profile: str) -> frozenset[int]:
    return OFFERED_WEEKDAYS_BY_PROFILE.get(policy_profile, OFFERED_WEEKDAYS["normal"])


def weekdays_for_selection_type(selection_type: str) -> frozenset[int]:
    return OFFERED_WEEKDAYS.get(selection_type, OFFERED_WEEKDAYS["normal"])


CALENDAR_LAYOUT: dict[str, str] = {
    "normal": "singles",
    "full_package": "package_pairs",
}

# Stable status codes returned to clients (do not rename without API version bump).
STATUS_AVAILABLE = "available"
STATUS_CAPACITY_FULL = "capacity_full"
STATUS_NO_SLOTS = "no_slots"
STATUS_NOT_OFFERED = "not_offered"
STATUS_CLOSED = "closed"

REASON_WRONG_DAY_TYPE = "wrong_day_type"
REASON_STUDIO_CLOSED = "studio_closed"
REASON_DAY_CAPACITY_REACHED = "day_capacity_reached"
REASON_NO_OPEN_TIMES = "no_open_times"


def iter_offered_dates(
    selection_key: str,
    *,
    start: date,
    horizon_end: date,
    count: int = CALENDAR_OFFERED_DAYS_COUNT,
    policy_profile: str | None = None,
) -> list[date]:
    """Next bookable weekdays for the selection, capped at *count* days."""
    if policy_profile:
        weekdays = weekdays_for_policy_profile(policy_profile)
    else:
        weekdays = weekdays_for_selection_type(selection_key)
    dates: list[date] = []
    cursor = start
    while cursor <= horizon_end and len(dates) < count:
        if cursor.weekday() in weekdays:
            dates.append(cursor)
        cursor += timedelta(days=1)
    return dates


def group_days_into_weeks(days: list[dict]) -> list[dict]:
    """Group day payloads by ISO week (Monday start) preserving order."""
    buckets: dict[str, list[dict]] = {}
    order: list[str] = []
    for day in days:
        current = date.fromisoformat(str(day["date"]))
        week_start = current - timedelta(days=current.weekday())
        key = week_start.isoformat()
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(day)
    return [{"week_start": key, "days": buckets[key]} for key in order]


def classify_calendar_day(
    *,
    selection_type: str,
    day_type: str,
    normal_bookings_allowed: bool,
    full_package_allowed: bool,
    max_clients: int,
    booked_clients: int,
    slot_count: int,
) -> dict:
    """Pure classification — same inputs always yield the same status payload."""
    capacity = {
        "max": max_clients,
        "booked": booked_clients,
        "remaining": max(0, max_clients - booked_clients),
    }
    base = {"slot_count": 0, "capacity": capacity}

    if day_type == "closed" or max_clients <= 0:
        return {
            **base,
            "status": STATUS_CLOSED,
            "reason_code": REASON_STUDIO_CLOSED,
            "capacity": {"max": 0, "booked": 0, "remaining": 0},
        }
    if selection_type == "normal" and not normal_bookings_allowed:
        return {
            **base,
            "status": STATUS_NOT_OFFERED,
            "reason_code": REASON_WRONG_DAY_TYPE,
            "capacity": {"max": 0, "booked": 0, "remaining": 0},
        }
    if selection_type == "full_package" and not full_package_allowed:
        return {
            **base,
            "status": STATUS_NOT_OFFERED,
            "reason_code": REASON_WRONG_DAY_TYPE,
            "capacity": {"max": 0, "booked": 0, "remaining": 0},
        }
    if booked_clients >= max_clients:
        return {
            **base,
            "status": STATUS_CAPACITY_FULL,
            "reason_code": REASON_DAY_CAPACITY_REACHED,
            "slot_count": 0,
            "capacity": capacity,
        }
    if slot_count <= 0:
        return {
            **base,
            "status": STATUS_NO_SLOTS,
            "reason_code": REASON_NO_OPEN_TIMES,
            "slot_count": 0,
            "capacity": capacity,
        }
    return {
        "status": STATUS_AVAILABLE,
        "reason_code": None,
        "slot_count": slot_count,
        "capacity": capacity,
    }
