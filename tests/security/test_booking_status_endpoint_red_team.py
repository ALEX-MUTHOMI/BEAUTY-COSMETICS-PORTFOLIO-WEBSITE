import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_status_endpoint_red_team_blocks_enumeration_pii_and_provider_leaks(settings, tmp_path):
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    booking, _session, ledger = _confirm_paid_booking("status-red-team")
    client = Client()

    valid = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    bad = client.get("/api/bookings/status/1/", secure=True)
    missing = client.get("/api/bookings/status/00000000-0000-4000-8000-000000000000/", secure=True)

    assert valid.status_code == 200
    assert bad.status_code == missing.status_code == 404
    assert bad.json() == missing.json()
    booking.refresh_from_db()
    body = valid.content.decode()
    forbidden = [
        "grace@example.com",
        "+254712345678",
        str(booking.id),
        str(ledger.id),
        booking.checkout_session_id,
        "provider-",
        "receipt-",
        "download_token",
    ]
    for value in forbidden:
        assert value
        assert value not in body
