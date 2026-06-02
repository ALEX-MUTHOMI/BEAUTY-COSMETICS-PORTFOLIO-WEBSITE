import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
@pytest.mark.latency
def test_booking_status_polling_100_times_is_stable_and_small(settings, tmp_path):
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("status-latency")
    client = Client()

    for _ in range(100):
        response = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
        assert response.status_code == 200
        assert len(response.content) < 1200
        assert b"grace@example.com" not in response.content
        assert b"+254" not in response.content
