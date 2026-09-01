import json

import pytest
from django.test import Client

from bookings.services.privacy_rights import BOOKING_PII_DATA_MAP, accept_privacy_rights_request


def test_booking_pii_data_map_covers_contractual_fields():
    assert set(BOOKING_PII_DATA_MAP) >= {"full_name", "email", "phone"}
    for _field, meta in BOOKING_PII_DATA_MAP.items():
        assert meta["purpose"]
        assert meta["lawful_basis"]
        assert meta["retention"]


@pytest.mark.django_db
def test_accept_privacy_rights_request_hashes_contact_and_returns_ticket():
    ticket = accept_privacy_rights_request(
        {
            "request_type": "access",
            "email": "grace@example.com",
            "phone": "+254712345678",
            "details": "Please export my booking data.",
        },
        correlation_id="corr-1",
    )
    assert ticket is not None
    assert ticket.status == "accepted"
    assert ticket.request_type == "access"
    assert len(ticket.ticket_id) == 20
    from bookings.models import PrivacyRightsRequest

    row = PrivacyRightsRequest.objects.get(ticket_id=ticket.ticket_id)
    assert row.email_hash_hmac
    assert row.phone_hash_hmac
    assert "grace@" not in row.email_hash_hmac
    assert "+254" not in row.phone_hash_hmac


@pytest.mark.django_db
def test_accept_privacy_rights_request_rejects_invalid_type():
    assert accept_privacy_rights_request({"request_type": "dump_all", "email": "grace@example.com"}) is None


@pytest.mark.django_db
def test_privacy_rights_logs_never_contain_cleartext_pii(caplog):
    import logging

    with caplog.at_level(logging.INFO, logger="bookings.privacy_rights"):
        accept_privacy_rights_request(
            {
                "request_type": "erasure",
                "email": "grace@example.com",
                "phone": "+254712345678",
            },
            correlation_id="corr-pii",
        )
    joined = " ".join(r.message for r in caplog.records)
    assert "grace@example.com" not in joined
    assert "+254712345678" not in joined
    assert "privacy_rights_accepted" in joined


@pytest.mark.django_db
def test_privacy_data_map_endpoint_is_public_and_contains_no_customer_rows(client):
    response = client.get("/api/bookings/privacy/data-map/", secure=True)
    assert response.status_code == 200
    payload = response.json()
    assert "email" in payload["data_map"]
    assert "Kenya-DPA-2019" in payload["jurisdiction"]
    serialized = json.dumps(payload)
    assert "grace@" not in serialized
    assert "+254" not in serialized


@pytest.mark.django_db
def test_privacy_rights_post_requires_csrf_and_does_not_echo_pii():
    client = Client(enforce_csrf_checks=True)
    csrf = client.get("/api/csrf/", secure=True)
    token = csrf.json()["csrf_token"]
    response = client.post(
        "/api/bookings/privacy/rights-request/",
        data=json.dumps(
            {
                "request_type": "erasure",
                "email": "grace@example.com",
                "phone": "+254712345678",
            }
        ),
        content_type="application/json",
        secure=True,
        HTTP_X_CSRFTOKEN=token,
        HTTP_REFERER="https://testserver/",
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert "grace@example.com" not in json.dumps(body)
    assert "+254712345678" not in json.dumps(body)


@pytest.mark.django_db
def test_privacy_rights_post_without_csrf_is_forbidden():
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        "/api/bookings/privacy/rights-request/",
        data=json.dumps({"request_type": "access", "email": "grace@example.com"}),
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_public_status_payload_excludes_customer_contact_pii():
    """Need-to-know: status JSON must not expose email/phone (DPA minimization)."""
    from bookings.tests.factories import create_booking

    booking = create_booking()
    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)
    assert response.status_code == 200
    payload = response.json()
    assert "phone" not in payload
    assert "email" not in payload
    assert "customer" not in payload
    serialized = json.dumps(payload)
    assert "+254" not in serialized
    assert "@" not in serialized
