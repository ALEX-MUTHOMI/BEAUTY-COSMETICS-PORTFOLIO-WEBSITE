import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_status_portal_does_not_leak_pii_internal_ids_or_provider_refs(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, session, ledger = _confirm_paid_booking("status-security-b5")

    payload = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True).json()
    surface = str(payload)

    assert str(booking.id) not in surface
    assert str(session.id) not in surface
    assert str(ledger.id) not in surface
    assert "grace@example.com" not in surface
    assert "+254" not in surface
    assert "CheckoutRequestID" not in surface
    assert "receipt-" not in surface.lower()


@pytest.mark.django_db(transaction=True)
def test_status_portal_polling_is_read_only_and_generic_for_bad_ids(settings, tmp_path):
    """Prove polling is read-only and bad IDs get generic 404s.

    The booking_status throttle is raised for this durability test only.
    Production limit remains 30/min (Phase 3D).
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["booking_status"] = "200/min"
    booking, _session, _ledger = _confirm_paid_booking("status-polling-b5")
    client = Client()

    booking.refresh_from_db()
    before = booking.updated_at
    for _ in range(100):
        assert client.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code == 200
    booking.refresh_from_db()
    assert booking.updated_at == before

    malformed = client.get("/api/bookings/status/not-a-uuid/", secure=True)
    missing = client.get("/api/bookings/status/00000000-0000-4000-8000-000000000000/", secure=True)
    assert malformed.status_code == missing.status_code == 404
    assert malformed.json() == missing.json()
