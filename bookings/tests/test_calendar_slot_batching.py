"""Phase B: calendar slot fetching must not be O(days) availability calls."""

from datetime import date, timedelta

from bookings.services.availability import MAX_AVAILABILITY_RANGE_DAYS
from bookings.services.booking_calendar import _partition_dates_for_availability


def test_partition_keeps_span_within_availability_max():
    start = date(2030, 1, 1)
    dates = [start + timedelta(days=i) for i in range(20)]
    batches = _partition_dates_for_availability(dates)
    assert len(batches) >= 2
    for batch in batches:
        assert (batch[-1] - batch[0]).days + 1 <= MAX_AVAILABILITY_RANGE_DAYS


def test_partition_batches_fewer_than_day_count_when_dense():
    start = date(2030, 6, 2)
    dates = [start + timedelta(days=i) for i in range(8)]
    batches = _partition_dates_for_availability(dates)
    assert len(batches) == 1
    assert len(batches[0]) == 8


def test_partition_empty():
    assert _partition_dates_for_availability([]) == []
