"""Hybrid yield scheduling — dynamic single quota + duration-stepped package anchors."""

from __future__ import annotations

from datetime import datetime, time, timedelta

# Safety ceiling for short singles (prevents API blowups / over-booking spam).
DYNAMIC_MAX_CLIENTS_CEILING = 16
PACKAGE_MAX_CLIENTS = 3


def business_minutes_between(start: time, end: time) -> int:
    """Minutes from *start* to *end* on the same calendar day."""
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def compute_dynamic_max_clients(
    business_minutes: int,
    duration_minutes: int,
    turnaround_minutes: int = 0,
    *,
    ceiling: int = DYNAMIC_MAX_CLIENTS_CEILING,
) -> int:
    """
    Single-treatment daily yield:
    floor(available_minutes / (duration + turnaround)), capped by *ceiling*.
    """
    if business_minutes <= 0 or duration_minutes <= 0 or ceiling <= 0:
        return 0
    block = duration_minutes + max(0, turnaround_minutes)
    if block <= 0:
        return 0
    return min(business_minutes // block, ceiling)


def resolve_day_client_cap(
    *,
    selection_type: str,
    max_clients_policy: int,
    business_start: time,
    business_end: time,
    duration_minutes: int = 0,
    turnaround_minutes: int = 0,
    package_max_clients: int = PACKAGE_MAX_CLIENTS,
) -> int:
    """
    Effective client cap for a day.

    Packages: fixed policy max (default 3).
    Singles with known duration: dynamic yield.
    Singles without duration: fall back to policy max_clients.
    """
    if max_clients_policy <= 0:
        return 0
    if selection_type == "full_package":
        return min(max_clients_policy, package_max_clients) if max_clients_policy else 0
    if duration_minutes <= 0:
        return max_clients_policy
    minutes = business_minutes_between(business_start, business_end)
    return compute_dynamic_max_clients(minutes, duration_minutes, turnaround_minutes)


def generate_duration_stepped_anchors(
    business_start: datetime,
    business_end: datetime,
    duration_minutes: int,
    buffer_before_minutes: int,
    buffer_after_minutes: int,
    max_clients: int,
) -> list[tuple[datetime, datetime]]:
    """
    Macro-packing for full packages: start at open (+ before), then step by
    duration + turnaround. Returns (service_start, service_end) pairs.
    """
    if duration_minutes <= 0 or max_clients <= 0:
        return []
    turnaround = max(0, buffer_before_minutes) + max(0, buffer_after_minutes)
    block = timedelta(minutes=duration_minutes + turnaround)
    duration = timedelta(minutes=duration_minutes)
    before = timedelta(minutes=max(0, buffer_before_minutes))
    after = timedelta(minutes=max(0, buffer_after_minutes))

    anchors: list[tuple[datetime, datetime]] = []
    cursor = business_start + before
    while len(anchors) < max_clients:
        service_end = cursor + duration
        if cursor - before < business_start or service_end + after > business_end:
            break
        anchors.append((cursor, service_end))
        cursor = cursor + block
    return anchors


def filter_candidates_to_free_intervals(
    candidates: list[tuple[datetime, datetime]],
    free_intervals: list[tuple[datetime, datetime]],
    buffer_before_minutes: int = 0,
    buffer_after_minutes: int = 0,
) -> list[tuple[datetime, datetime]]:
    """Keep candidates whose full buffered window fits inside a free interval."""
    if not candidates or not free_intervals:
        return []
    before = timedelta(minutes=max(0, buffer_before_minutes))
    after = timedelta(minutes=max(0, buffer_after_minutes))
    kept: list[tuple[datetime, datetime]] = []
    for start, end in candidates:
        window_start = start - before
        window_end = end + after
        for free_start, free_end in free_intervals:
            if window_start >= free_start and window_end <= free_end:
                kept.append((start, end))
                break
    return kept
