import copy

import pytest
from django.test import Client, override_settings

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
def test_booking_status_endpoint_polling_is_read_only_and_bounded(django_assert_num_queries, settings):
    """Prove the status endpoint is read-only: 100 GETs must not change updated_at.

    The booking_status throttle is raised for this durability test only.
    Production limit remains 30/min (Phase 3D).
    """
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["booking_status"] = "200/min"
    with override_settings(REST_FRAMEWORK=rest_framework):
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

    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["booking_status"] == "20/min"


@pytest.mark.django_db(transaction=True)
def test_booking_status_throttle_is_generic_and_actor_isolated(settings, tmp_path):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["booking_status"] = "1/min"
    with override_settings(REST_FRAMEWORK=rest_framework):
        booking, _session, _ledger = _confirm_paid_booking("status-throttle")
        client = Client()
        first = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True, REMOTE_ADDR="203.0.113.10")
        blocked = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True, REMOTE_ADDR="203.0.113.10")
        other_actor = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True, REMOTE_ADDR="203.0.113.11")

    assert first.status_code == 200
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert "Retry-After" in blocked
    assert other_actor.status_code == 200
    assert all(marker not in blocked.content.lower() for marker in (b"token", b"storage", b"provider", b"traceback"))
