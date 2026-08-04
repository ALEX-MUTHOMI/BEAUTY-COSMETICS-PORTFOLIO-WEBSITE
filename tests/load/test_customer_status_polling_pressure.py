import copy

import pytest
from django.test import Client, override_settings

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_customer_status_polling_pressure_is_read_only_and_bounded(settings):
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["booking_status"] = "1200/min"
    with override_settings(REST_FRAMEWORK=rest_framework):
        booking, _session, _ledger = _confirm_paid_booking("status-pressure-b5")
        client = Client()
        booking.refresh_from_db()
        before = booking.updated_at

        for _ in range(1000):
            response = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
            assert response.status_code == 200

        booking.refresh_from_db()
        assert booking.updated_at == before

    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["booking_status"] == "20/min"
