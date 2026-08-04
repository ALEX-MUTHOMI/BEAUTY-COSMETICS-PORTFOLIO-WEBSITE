import copy

import pytest
from django.test import Client, override_settings

from bookings.tests.factories import create_booking
from bookings.tests.time_helpers import valid_business_start_utc


@pytest.mark.django_db
@pytest.mark.latency
def test_status_page_policy_payload_is_small_and_redacted_under_polling(settings):
    # Durability probe — raise throttle for this test only; runtime stays 20/min.
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["booking_status"] = "200/min"
    booking = create_booking(starts_at=valid_business_start_utc(), status="confirmed")
    client = Client()

    with override_settings(REST_FRAMEWORK=rest_framework):
        for _ in range(25):
            response = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
            assert response.status_code == 200
            assert len(response.content) < 4096
            assert b"grace@example.com" not in response.content
            assert b"+254712345678" not in response.content
