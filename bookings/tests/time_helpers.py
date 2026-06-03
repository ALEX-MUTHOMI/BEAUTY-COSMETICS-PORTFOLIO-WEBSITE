from datetime import datetime
from zoneinfo import ZoneInfo

NAIROBI = ZoneInfo("Africa/Nairobi")
UTC = ZoneInfo("UTC")


def make_eat_datetime(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=NAIROBI)


def make_utc_from_eat(year, month, day, hour, minute=0):
    return make_eat_datetime(year, month, day, hour, minute).astimezone(UTC)


def valid_business_start_utc():
    # Tuesday 10:00 EAT, far enough from the B5 cutoff window without using now()+offset.
    return make_utc_from_eat(2030, 6, 4, 10, 0)


def valid_reschedule_start_utc():
    # Wednesday 10:00 EAT; deterministic replacement slot for lifecycle tests.
    return make_utc_from_eat(2030, 6, 5, 10, 0)
