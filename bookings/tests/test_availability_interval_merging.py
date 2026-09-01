from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

NAIROBI = ZoneInfo("Africa/Nairobi")


def _module():
    try:
        from bookings.services import availability
    except ImportError as exc:
        pytest.fail(f"availability module missing: {exc}")
    return availability


def _dt(hour, minute=0):
    day = timezone.localdate() + timedelta(days=7)
    return datetime.combine(day, datetime.min.time(), tzinfo=NAIROBI).replace(hour=hour, minute=minute)


def test_merge_intervals_combines_overlaps_but_not_adjacent_ranges():
    availability = _module()
    intervals = [
        (_dt(9), _dt(10)),
        (_dt(9, 30), _dt(11)),
        (_dt(11), _dt(12)),
    ]

    merged = availability.merge_intervals(intervals)

    assert merged == [(_dt(9), _dt(11)), (_dt(11), _dt(12))]


def test_subtract_busy_intervals_returns_only_free_windows():
    availability = _module()
    free = availability.subtract_intervals(
        [(_dt(7), _dt(12))],
        [(_dt(8), _dt(9)), (_dt(9, 30), _dt(10, 30))],
    )

    assert free == [(_dt(7), _dt(8)), (_dt(9), _dt(9, 30)), (_dt(10, 30), _dt(12))]


def test_candidate_generation_uses_free_intervals_only():
    availability = _module()
    candidates = availability.generate_candidates_from_free_intervals(
        [(_dt(7), _dt(9)), (_dt(10), _dt(12))],
        duration_minutes=60,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        slot_interval_minutes=30,
    )

    starts = [candidate[0].strftime("%H:%M") for candidate in candidates]
    assert starts == ["07:00", "07:30", "08:00", "10:00", "10:30", "11:00"]


def test_candidates_with_buffers_never_overlap_busy_core():
    """Invariant: buffered service windows stay inside free intervals only."""
    availability = _module()
    free = availability.subtract_intervals(
        [(_dt(7), _dt(12))],
        [(_dt(9), _dt(10))],
    )
    candidates = availability.generate_candidates_from_free_intervals(
        free,
        duration_minutes=60,
        buffer_before_minutes=15,
        buffer_after_minutes=15,
        slot_interval_minutes=30,
    )
    before = timedelta(minutes=15)
    after = timedelta(minutes=15)
    busy = [(_dt(9), _dt(10))]
    for start, end in candidates:
        window_start = start - before
        window_end = end + after
        for busy_start, busy_end in busy:
            assert window_end <= busy_start or window_start >= busy_end
