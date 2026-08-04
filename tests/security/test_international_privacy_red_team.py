import pytest

from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import valid_business_start_utc
from bookings.views import _status_payload


@pytest.mark.django_db
def test_status_payload_keeps_nairobi_as_appointment_truth_for_international_customers():
    booking = create_booking(starts_at=valid_business_start_utc())

    payload = _status_payload(booking)

    assert payload["schedule"]["start_time_eat"] == "10:00 AM"
    assert payload["schedule"]["timezone"] == "Africa/Nairobi"
    assert "grace@example.com" not in str(payload)
    assert "+254712345678" not in str(payload)
