import json
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.test import Client

from bookings.models import Booking
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.factories import create_booking, create_service_resource_customer
from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    INTERNAL_DEBUG_KEY_MARKERS,
    KNOWN_TEST_PII_VALUES,
    PAYMENT_PROVIDER_KEY_MARKERS,
    STORAGE_KEY_MARKERS,
    assert_response_excludes_categories,
)

NAIROBI = ZoneInfo("Africa/Nairobi")


def _future_monday(hour=9):
    return datetime.combine(date(2026, 8, 3), time(hour, 0), tzinfo=NAIROBI)


def _hold_payload(service, resource, *, idempotency_key="phase-3c-hold"):
    return {
        "selection_type": "normal",
        "service_public_id": str(service.id),
        "resource_public_id": str(resource.id),
        "starts_at": _future_monday().isoformat(),
        "customer": {
            "full_name": "Grace Wanjiku",
            "email": "grace@example.com",
            "phone": "+254712345678",
        },
        "idempotency_key": idempotency_key,
    }


def _policy_acceptance():
    ensure_default_legal_documents()
    return {
        "accepted": True,
        "checkbox_text": POLICY_ACCEPTANCE_TEXT,
        "locale": "en-KE",
        "timezone_name": "Africa/Nairobi",
        "country_hint": "KE",
    }


@pytest.mark.django_db
def test_booking_hold_response_is_public_safe_and_minimized():
    service, resource, _customer = create_service_resource_customer()

    response = Client().post(
        "/api/bookings/holds/",
        data=json.dumps(_hold_payload(service, resource)),
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 201
    payload = assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES,
    )
    assert set(payload["booking"]).issubset(
        {
            "booking_public_id",
            "status",
            "hold_expires_at",
            "starts_at",
            "ends_at",
            "selection",
            "next_action",
            "hold_ttl_minutes",
        }
    )


@pytest.mark.django_db
def test_booking_checkout_bridge_response_exposes_only_customer_next_action_fields():
    service, resource, _customer = create_service_resource_customer()
    client = Client()
    hold_response = client.post(
        "/api/bookings/holds/",
        data=json.dumps(_hold_payload(service, resource, idempotency_key="phase-3c-checkout-hold")),
        content_type="application/json",
        secure=True,
    )
    booking_public_id = hold_response.json()["booking"]["booking_public_id"]

    response = client.post(
        "/api/bookings/checkout/",
        data=json.dumps(
            {
                "booking_public_id": booking_public_id,
                "idempotency_key": "phase-3c-checkout",
                "policy_acceptance": _policy_acceptance(),
            }
        ),
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 201
    payload = assert_response_excludes_categories(
        response,
        categories=(AUTH_KEY_MARKERS, STORAGE_KEY_MARKERS, INTERNAL_DEBUG_KEY_MARKERS),
        forbidden_values=KNOWN_TEST_PII_VALUES,
        allowed_keys={"checkout_public_id"},
    )
    assert set(payload["checkout"]).issubset(
        {
            "booking_public_id",
            "status_url",
            "status_api_url",
            "checkout_public_id",
            "booking_status",
            "payment_status",
            "amount",
            "currency",
            "next_action",
        }
    )
    rendered = response.content.decode("utf-8")
    assert "provider_reference" not in rendered
    assert "raw_payload" not in rendered
    assert "ledger" not in rendered


@pytest.mark.django_db
def test_public_booking_status_response_is_zero_pii_and_provider_free():
    booking = create_booking(status=Booking.Status.PAYMENT_PENDING)
    booking.checkout_session_id = "phase-3c-hidden-checkout-session"
    booking.save(update_fields=["checkout_session_id", "updated_at"])

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)

    assert response.status_code == 200
    payload = assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        allowed_keys={"requires_otp"},
        forbidden_values=KNOWN_TEST_PII_VALUES | {booking.checkout_session_id, str(booking.id)},
    )
    assert set(payload).issubset(
        {
            "booking_reference",
            "booking_status",
            "payment_status",
            "receipt_status",
            "email_status",
            "reminder_status",
            "reschedule",
            "schedule",
            "service",
            "next_action",
        }
    )


@pytest.mark.django_db
def test_denied_booking_status_response_is_generic_and_non_leaky():
    response = Client().get("/api/bookings/status/not-a-valid-token/", secure=True)

    assert response.status_code == 404
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"not-a-valid-token"},
    )
