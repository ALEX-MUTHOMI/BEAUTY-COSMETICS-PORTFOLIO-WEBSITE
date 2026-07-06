"""Deterministic public booking calendar — domain constants and classification."""

from __future__ import annotations

MAX_CALENDAR_RANGE_DAYS = 42
CALENDAR_TIMEZONE = "Africa/Nairobi"

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
