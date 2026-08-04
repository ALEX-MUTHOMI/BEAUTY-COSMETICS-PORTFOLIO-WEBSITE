from bookings.tests.time_helpers import make_eat_datetime, make_utc_from_eat


def test_make_utc_from_eat_preserves_nairobi_business_time():
    value = make_utc_from_eat(2026, 6, 9, 10, 0)

    assert value.hour == 7
    assert value.minute == 0
    assert make_eat_datetime(2026, 6, 9, 10, 0).utcoffset().total_seconds() == 3 * 60 * 60
