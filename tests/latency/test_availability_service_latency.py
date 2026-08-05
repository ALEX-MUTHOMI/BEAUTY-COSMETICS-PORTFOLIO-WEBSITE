"""Latency gates for availability builds (Backend DSA Efficiency Phase A)."""

import statistics
import time
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from bookings.services.availability import AvailabilityService
from bookings.tests.factories import create_service_resource_customer

AVAILABILITY_P95_BUDGET_SECONDS = 2.0
AVAILABILITY_SINGLE_DAY_MAX_QUERIES = 40
AVAILABILITY_FOURTEEN_DAY_MAX_QUERIES = 80
WARMUP = 1
MEASURE = 8


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = max(0, int(0.95 * (len(ordered) - 1)))
    return ordered[index]


@pytest.mark.django_db
@pytest.mark.latency
def test_availability_single_day_query_count_is_bounded():
    service, _resource, _customer = create_service_resource_customer()
    day = timezone.localdate() + timedelta(days=7)

    with CaptureQueriesContext(connection) as captured:
        rows = AvailabilityService.get_available_slots(service.id, day, day)

    assert len(rows) == 1
    assert len(captured) <= AVAILABILITY_SINGLE_DAY_MAX_QUERIES


@pytest.mark.django_db
@pytest.mark.latency
def test_availability_fourteen_day_query_count_is_bounded():
    service, _resource, _customer = create_service_resource_customer()
    start = timezone.localdate() + timedelta(days=7)
    end = start + timedelta(days=13)

    with CaptureQueriesContext(connection) as captured:
        rows = AvailabilityService.get_available_slots(service.id, start, end)

    assert len(rows) == 14
    assert len(captured) <= AVAILABILITY_FOURTEEN_DAY_MAX_QUERIES


@pytest.mark.django_db
@pytest.mark.latency
def test_availability_single_day_under_p95_budget():
    service, _resource, _customer = create_service_resource_customer()
    day = timezone.localdate() + timedelta(days=7)

    for _ in range(WARMUP):
        AvailabilityService.get_available_slots(service.id, day, day)

    durations = []
    for _ in range(MEASURE):
        started = time.perf_counter()
        AvailabilityService.get_available_slots(service.id, day, day)
        durations.append(time.perf_counter() - started)

    assert _p95(durations) < AVAILABILITY_P95_BUDGET_SECONDS
    assert statistics.median(durations) < AVAILABILITY_P95_BUDGET_SECONDS
