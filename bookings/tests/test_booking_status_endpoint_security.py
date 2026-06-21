import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_booking_status_endpoint_does_not_reflect_xss_or_internal_identifiers(settings, tmp_path):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("status-xss")
    booking.service.name = "<script>alert(1)</script> Bridal http://evil.test/a.css"
    booking.service.save(update_fields=["name", "updated_at"])

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    body = response.content.decode()

    assert response.status_code == 200
    assert "<script" not in body.lower()
    assert "http://evil.test" not in body
    assert str(booking.id) not in body
    booking.refresh_from_db()
    assert booking.checkout_session_id
    assert booking.checkout_session_id not in body
    assert "download_token" not in body


@pytest.mark.django_db(transaction=True)
def test_booking_status_endpoint_polling_is_read_only_and_bounded(
    django_assert_num_queries, settings
):
    """Prove the status endpoint is read-only: 100 GETs must not change updated_at.

    The booking_status throttle is raised for this durability test only.
    Production limit remains 30/min (Phase 3D).
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["booking_status"] = "200/min"
    booking, _session, _ledger = _confirm_paid_booking("status-polling")
    client = Client()

    with django_assert_num_queries(2):
        response = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)

    assert response.status_code == 200
    booking.refresh_from_db()
    original_updated_at = booking.updated_at
    for _ in range(100):
        assert client.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code == 200
    booking.refresh_from_db()
    assert booking.updated_at == original_updated_at
