from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework import status
from rest_framework.test import APIClient

from bookings.tests.factories import create_booking
from checkout.models import CheckoutSession
from checkout.services import create_checkout_session

User = get_user_model()


def _body(response):
    if hasattr(response, "data"):
        return str(response.data)
    return response.content.decode("utf-8", errors="replace")


def _assert_absent(response, markers):
    rendered = _body(response)
    for marker in markers:
        assert marker
        assert marker not in rendered


@pytest.mark.django_db
def test_customer_cannot_read_or_initiate_another_customers_checkout_with_tampered_identity():
    owner = User.objects.create_user(email="owner-3b@example.com", phone_number="+254700110001")
    attacker = User.objects.create_user(email="attacker-3b@example.com", phone_number="+254700110002")
    session = create_checkout_session(
        owner,
        Decimal("250.00"),
        "KES",
        "Private booking checkout",
        "booking",
        "private-booking-id",
        "phase-3b-owner-checkout",
    )

    client = APIClient()
    client.force_authenticate(user=attacker)
    hostile_headers = {
        "HTTP_X_USER_ID": str(owner.id),
        "HTTP_X_ROLE": "admin",
        "HTTP_X_ADMIN": "true",
    }

    detail = client.get(
        f"/api/checkout/sessions/{session.id}/?customer_id={owner.id}&scope=all",
        secure=True,
        **hostile_headers,
    )
    stk = client.post(
        f"/api/checkout/sessions/{session.id}/mpesa/stk/",
        {"phone_number": "+254700110099", "idempotency_key": "phase-3b-stk"},
        format="json",
        secure=True,
        **hostile_headers,
    )

    assert detail.status_code == status.HTTP_404_NOT_FOUND
    assert stk.status_code == status.HTTP_404_NOT_FOUND
    _assert_absent(detail, [str(session.id), "250.00", "private-booking-id", owner.email])
    _assert_absent(stk, [str(session.id), "250.00", "private-booking-id", owner.email])


@pytest.mark.django_db
def test_public_booking_status_token_is_public_safe_but_does_not_reveal_private_owner_data():
    booking = create_booking()
    booking.checkout_session_id = "not-a-real-checkout-session-id"
    booking.save(update_fields=["checkout_session_id", "updated_at"])

    response = Client().get(f"/api/bookings/status/{booking.public_id}/", secure=True)

    assert response.status_code == 200
    _assert_absent(
        response,
        [
            "grace@example.com",
            "+254712345678",
            str(booking.id),
            booking.checkout_session_id,
            "customer_profile",
            "provider_reference",
            "ledger",
        ],
    )


@pytest.mark.django_db
def test_invalid_and_missing_booking_status_tokens_are_indistinguishable_and_generic():
    client = Client()

    malformed = client.get("/api/bookings/status/not-a-token/", secure=True)
    missing = client.get("/api/bookings/status/00000000-0000-4000-8000-000000000000/", secure=True)

    assert malformed.status_code == missing.status_code == 404
    assert malformed.json() == missing.json()
    _assert_absent(malformed, ["Traceback", "ValidationError", "DoesNotExist", "public_id"])
    _assert_absent(missing, ["Traceback", "ValidationError", "DoesNotExist", "public_id"])


@pytest.mark.django_db
def test_disabled_legacy_billing_stk_route_cannot_be_used_to_target_payment_objects():
    response = APIClient().post(
        "/api/billing/stk-push/",
        {
            "checkout_request_id": "attacker-provider-id",
            "ledger_id": "attacker-ledger-id",
            "amount": "1.00",
        },
        format="json",
        secure=True,
    )

    assert response.status_code == status.HTTP_410_GONE
    rendered = str(response.data)
    assert "attacker-provider-id" not in rendered
    assert "attacker-ledger-id" not in rendered
    assert CheckoutSession.objects.count() == 0
