"""Latency gates for catalog-aware calendar builds (Phase 3c)."""

import statistics
import time

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from bookings.services.booking_calendar import BookingCalendarService
from bookings.tests.factories import create_service_resource_customer

CALENDAR_P95_BUDGET_SECONDS = 2.0
CALENDAR_WARMUP_ITERATIONS = 2
CALENDAR_MEASURE_ITERATIONS = 11
CALENDAR_MAX_QUERIES = 120


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = max(0, int(0.95 * (len(ordered) - 1)))
    return ordered[index]


@pytest.mark.django_db
@pytest.mark.latency
def test_calendar_default_range_query_count_is_bounded():
    service, _resource, _customer = create_service_resource_customer()

    with CaptureQueriesContext(connection) as captured:
        payload = BookingCalendarService.build_calendar(
            selection_type="normal",
            service_public_id=str(service.id),
        )

    assert len(payload["days"]) == 8
    assert len(captured) <= CALENDAR_MAX_QUERIES


@pytest.mark.django_db
@pytest.mark.latency
def test_calendar_slot_batching_keeps_queries_far_below_per_day_n_plus_one():
    """Batched availability must beat naive O(days) slot fetches (Concept 20)."""
    service, _resource, _customer = create_service_resource_customer()

    with CaptureQueriesContext(connection) as captured:
        payload = BookingCalendarService.build_calendar(
            selection_type="normal",
            service_public_id=str(service.id),
        )

    days_needing = sum(1 for day in payload["days"] if day["capacity"]["booked"] < day["capacity"]["max"])
    # One query group per availability window, not one full availability stack per day.
    # Allow headroom for policy/hours reads but stay well under 8× single-day cost.
    assert days_needing >= 1
    assert len(captured) < max(40, days_needing * 15)


@pytest.mark.django_db
@pytest.mark.latency
def test_calendar_default_range_under_p95_budget():
    service, _resource, _customer = create_service_resource_customer()

    for _ in range(CALENDAR_WARMUP_ITERATIONS):
        BookingCalendarService.build_calendar(
            selection_type="normal",
            service_public_id=str(service.id),
        )

    durations = []
    for _ in range(CALENDAR_MEASURE_ITERATIONS):
        started = time.perf_counter()
        payload = BookingCalendarService.build_calendar(
            selection_type="normal",
            service_public_id=str(service.id),
        )
        durations.append(time.perf_counter() - started)
        assert len(payload["days"]) == 8

    assert _p95(durations) < CALENDAR_P95_BUDGET_SECONDS
    assert statistics.median(durations) < CALENDAR_P95_BUDGET_SECONDS


@pytest.mark.django_db
@pytest.mark.latency
def test_calendar_api_default_range_under_p95_budget():
    service, _resource, _customer = create_service_resource_customer()
    client = Client()

    for _ in range(CALENDAR_WARMUP_ITERATIONS):
        response = client.get(
            "/api/bookings/calendar/",
            {"selection_type": "normal", "service_public_id": str(service.id)},
            secure=True,
        )
        assert response.status_code == 200

    durations = []
    for _ in range(CALENDAR_MEASURE_ITERATIONS):
        started = time.perf_counter()
        response = client.get(
            "/api/bookings/calendar/",
            {"selection_type": "normal", "service_public_id": str(service.id)},
            secure=True,
        )
        durations.append(time.perf_counter() - started)
        assert response.status_code == 200
        assert len(response.json()["calendar"]["days"]) == 8

    assert _p95(durations) < CALENDAR_P95_BUDGET_SECONDS
