import copy

import pytest
from django.test import Client, override_settings

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_customer_status_kenya_latency_retries_do_not_mutate_state(settings):
    # Durability probe — raise throttle for this test only; runtime stays 20/min.
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["booking_status"] = "200/min"
    booking, _session, _ledger = _confirm_paid_booking("status-kenya-latency-b5")
    client = Client()
    booking.refresh_from_db()
    before = booking.updated_at

    with override_settings(REST_FRAMEWORK=rest_framework):
        for _ in range(25):
            response = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
            assert response.status_code == 200
            assert response["Cache-Control"] == "no-store"

    booking.refresh_from_db()
    assert booking.updated_at == before
