"""Red-team: hold endpoint must enforce Turnstile under abuse (not UI-only)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.test import Client

from bookings.domain.circuit_breaker import BookingCircuitBreaker
from bookings.models import BookingPolicy


def _csrf_client():
    client = Client(enforce_csrf_checks=True)
    response = client.get("/api/csrf/", secure=True)
    assert response.status_code == 200
    return client, response.json()["csrf_token"]


def _post_json(client, path, payload, csrf_token):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_REFERER="https://testserver/",
        secure=True,
    )


def _hold_payload(**overrides):
    body = {
        "selection_type": "normal",
        "service_public_id": "11111111-1111-4111-8111-111111111111",
        "resource_public_id": "22222222-2222-4222-8222-222222222222",
        "starts_at": "2026-07-15T09:00:00+03:00",
        "idempotency_key": "redteam-hold-1",
        "customer": {
            "full_name": "Red Team",
            "email": "redteam@example.invalid",
            "phone": "+254700000001",
        },
    }
    body.update(overrides)
    return body


class FakeAbuseRedis:
    def get(self, key):
        if key == BookingCircuitBreaker.CREATED_KEY:
            return b"25"
        if key == BookingCircuitBreaker.CONFIRMED_KEY:
            return b"0"
        return None

    def incr(self, key):
        return 1

    def expire(self, key, seconds):
        return True


@pytest.mark.django_db(transaction=True)
def test_hold_rejects_missing_turnstile_when_circuit_is_abuse():
    BookingPolicy.objects.create(default_hold_minutes=10, abuse_hold_minutes=3, require_turnstile_under_abuse=True)
    client, csrf_token = _csrf_client()

    with (
        patch("bookings.api.public_views._get_redis_client_safe", return_value=FakeAbuseRedis()),
        patch("users.services.OTPService.verify_turnstile_token", return_value=False),
        patch("bookings.services.holds.BookingHoldService.create_hold") as create_hold,
    ):
        response = _post_json(client, "/api/bookings/holds/", _hold_payload(), csrf_token)

    assert response.status_code == 400
    assert response.json()["detail"] == "Booking request could not be accepted."
    create_hold.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_hold_accepts_valid_turnstile_under_abuse_before_service_call():
    BookingPolicy.objects.create(default_hold_minutes=10, abuse_hold_minutes=3, require_turnstile_under_abuse=True)
    client, csrf_token = _csrf_client()

    with (
        patch("bookings.api.public_views._get_redis_client_safe", return_value=FakeAbuseRedis()),
        patch("users.services.OTPService.verify_turnstile_token", return_value=True) as verify,
        patch("bookings.services.holds.BookingHoldService.create_hold") as create_hold,
    ):
        create_hold.side_effect = ValidationError("stop-after-turnstile")
        response = _post_json(
            client,
            "/api/bookings/holds/",
            _hold_payload(turnstile_token="CF_CLEARANCE_TEST_TOKEN"),
            csrf_token,
        )

    assert response.status_code == 400
    verify.assert_called_once()
    create_hold.assert_called_once()
