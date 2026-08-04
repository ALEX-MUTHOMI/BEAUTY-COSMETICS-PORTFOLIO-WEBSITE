"""Unit tests for hybrid yield scheduling math (no DB)."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from bookings.domain.yield_scheduling import (
    DYNAMIC_MAX_CLIENTS_CEILING,
    business_minutes_between,
    compute_dynamic_max_clients,
    filter_candidates_to_free_intervals,
    generate_duration_stepped_anchors,
    resolve_day_client_cap,
)

NAIROBI = ZoneInfo("Africa/Nairobi")


def _day_at(hour, minute=0):
    return datetime(2026, 7, 7, hour, minute, tzinfo=NAIROBI)


def test_business_minutes_default_shift():
    assert business_minutes_between(time(7, 0), time(19, 0)) == 720


def test_dynamic_max_half_leg_style_45_plus_15():
    assert compute_dynamic_max_clients(720, 45, 15) == 12


def test_dynamic_max_90_plus_15():
    assert compute_dynamic_max_clients(720, 90, 15) == 6


def test_dynamic_max_short_treatment_hits_ceiling():
    assert compute_dynamic_max_clients(720, 15, 0) == DYNAMIC_MAX_CLIENTS_CEILING


def test_dynamic_max_zero_duration_returns_zero():
    assert compute_dynamic_max_clients(720, 0, 15) == 0


def test_resolve_package_cap_fixed_at_three():
    assert (
        resolve_day_client_cap(
            selection_type="full_package",
            max_clients_policy=3,
            business_start=time(7, 0),
            business_end=time(19, 0),
            duration_minutes=240,
            turnaround_minutes=0,
        )
        == 3
    )


def test_resolve_single_cap_dynamic_when_duration_known():
    assert (
        resolve_day_client_cap(
            selection_type="normal",
            max_clients_policy=5,
            business_start=time(7, 0),
            business_end=time(19, 0),
            duration_minutes=45,
            turnaround_minutes=15,
        )
        == 12
    )


def test_resolve_single_cap_falls_back_to_policy_without_duration():
    assert (
        resolve_day_client_cap(
            selection_type="normal",
            max_clients_policy=5,
            business_start=time(7, 0),
            business_end=time(19, 0),
            duration_minutes=0,
            turnaround_minutes=0,
        )
        == 5
    )


def test_classic_package_anchors_240():
    anchors = generate_duration_stepped_anchors(
        _day_at(7),
        _day_at(19),
        duration_minutes=240,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        max_clients=3,
    )
    starts = [row[0].strftime("%H:%M") for row in anchors]
    assert starts == ["07:00", "11:00", "15:00"]


def test_glow_package_anchors_180():
    anchors = generate_duration_stepped_anchors(
        _day_at(7),
        _day_at(19),
        duration_minutes=180,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        max_clients=3,
    )
    starts = [row[0].strftime("%H:%M") for row in anchors]
    assert starts == ["07:00", "10:00", "13:00"]


def test_relax_package_anchors_150():
    anchors = generate_duration_stepped_anchors(
        _day_at(7),
        _day_at(19),
        duration_minutes=150,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        max_clients=3,
    )
    starts = [row[0].strftime("%H:%M") for row in anchors]
    assert starts == ["07:00", "09:30", "12:00"]


def test_stepped_anchors_never_offer_mid_morning_fragment():
    anchors = generate_duration_stepped_anchors(
        _day_at(7),
        _day_at(19),
        duration_minutes=180,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        max_clients=3,
    )
    starts = {row[0].strftime("%H:%M") for row in anchors}
    assert "08:30" not in starts
    assert "09:00" not in starts


def test_filter_anchors_drops_occupied_morning_block():
    anchors = generate_duration_stepped_anchors(
        _day_at(7),
        _day_at(19),
        duration_minutes=180,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        max_clients=3,
    )
    # 07:00–10:00 booked → free from 10:00 onward
    free = [(_day_at(10), _day_at(19))]
    kept = filter_candidates_to_free_intervals(anchors, free)
    starts = [row[0].strftime("%H:%M") for row in kept]
    assert starts == ["10:00", "13:00"]
