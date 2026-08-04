import pytest

from bookings.models import BookingDayPolicy
from bookings.services.day_policy import default_policy_for_date
from bookings.tests.test_b6_helpers import eat_datetime


@pytest.mark.django_db
def test_default_day_policy_uses_africa_nairobi_weekday_rules():
    assert default_policy_for_date(eat_datetime(2030, 6, 3, 9).date()).day_type == BookingDayPolicy.DayType.NORMAL
    assert default_policy_for_date(eat_datetime(2030, 6, 4, 9).date()).day_type == BookingDayPolicy.DayType.FULL_PACKAGE
    assert default_policy_for_date(eat_datetime(2030, 6, 9, 9).date()).day_type == BookingDayPolicy.DayType.CLOSED
