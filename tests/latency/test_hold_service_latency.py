"""Latency gates for hold create (Backend DSA Efficiency Phase A)."""

import statistics
import time as wall_time
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")
HOLD_P95_BUDGET_SECONDS = 2.0
HOLD_MAX_QUERIES = 60
WARMUP = 1
MEASURE = 5


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = max(0, int(0.95 * (len(ordered) - 1)))
    return ordered[index]


def _next_weekday_morning(weekday: int = 0) -> datetime:
    day = timezone.localdate() + timedelta(days=1)
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return datetime.combine(day, time(9, 0), tzinfo=NAIROBI)


@pytest.mark.django_db
@pytest.mark.latency
def test_hold_create_query_count_is_bounded():
    service, resource, _customer = create_service_resource_customer()
    starts_at = _next_weekday_morning()

    with CaptureQueriesContext(connection) as captured:
        BookingHoldService.create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=starts_at,
            customer_payload={"full_name": "Ada", "email": "ada-hold-lat@example.com", "phone": "+254700000001"},
            idempotency_key="hold-latency-queries",
        )

    assert len(captured) <= HOLD_MAX_QUERIES


@pytest.mark.django_db
@pytest.mark.latency
def test_hold_create_under_p95_budget():
    service, resource, _customer = create_service_resource_customer()
    base = _next_weekday_morning()

    for i in range(WARMUP):
        BookingHoldService.create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=base + timedelta(hours=i),
            customer_payload={
                "full_name": "Ada",
                "email": f"ada-hold-warm-{i}@example.com",
                "phone": f"+25470000001{i}",
            },
            idempotency_key=f"hold-latency-warm-{i}",
        )

    durations = []
    for i in range(MEASURE):
        starts_at = base + timedelta(hours=WARMUP + i)
        started = wall_time.perf_counter()
        BookingHoldService.create_hold(
            service_public_id=service.id,
            resource_public_id=resource.id,
            starts_at=starts_at,
            customer_payload={
                "full_name": "Ada",
                "email": f"ada-hold-meas-{i}@example.com",
                "phone": f"+25470000002{i}",
            },
            idempotency_key=f"hold-latency-meas-{i}",
        )
        durations.append(wall_time.perf_counter() - started)

    assert _p95(durations) < HOLD_P95_BUDGET_SECONDS
    assert statistics.median(durations) < HOLD_P95_BUDGET_SECONDS
