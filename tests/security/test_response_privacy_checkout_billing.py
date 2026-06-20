from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.services import create_checkout_session
from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    INTERNAL_DEBUG_KEY_MARKERS,
    KNOWN_TEST_PII_VALUES,
    PAYMENT_PROVIDER_KEY_MARKERS,
    STORAGE_KEY_MARKERS,
    assert_response_excludes_categories,
)

User = get_user_model()


def _client(user=None):
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    if user is not None:
        client.force_authenticate(user=user)
    return client


def _user(email="phase-3c-checkout@example.com", phone="+254700300001"):
    return User.objects.create_user(email=email, phone_number=phone)


@pytest.mark.django_db
def test_checkout_create_response_exposes_only_owner_safe_fields():
    customer = _user()
    response = _client(customer).post(
        "/api/checkout/sessions/",
        {
            "amount": "100.00",
            "currency": "KES",
            "description": "Phase 3C checkout",
            "purchasable_type": "booking_candidate",
            "purchasable_id": "phase-3c-booking-candidate",
            "idempotency_key": "phase-3c-checkout-create",
            "ledger_id": "attacker-ledger",
            "provider_reference": "attacker-provider-reference",
            "phone_number": "+254712345678",
        },
        format="json",
    )

    assert response.status_code == 201
    payload = assert_response_excludes_categories(
        response,
        categories=(AUTH_KEY_MARKERS, STORAGE_KEY_MARKERS, INTERNAL_DEBUG_KEY_MARKERS),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"attacker-ledger", "attacker-provider-reference"},
        allowed_keys={"id"},
    )
    assert set(payload).issubset({"id", "status"})
    assert CheckoutSession.objects.count() == 1
    assert LedgerTransaction.objects.count() == 0


@pytest.mark.django_db
def test_checkout_detail_and_cross_customer_denial_do_not_leak_provider_or_ledger_data():
    owner = _user("phase-3c-owner@example.com", "+254700300002")
    attacker = _user("phase-3c-attacker@example.com", "+254700300003")
    session = create_checkout_session(
        owner,
        Decimal("500.00"),
        "KES",
        "Private checkout",
        "booking",
        "private-booking-pk",
        "phase-3c-owner-session",
    )

    owner_response = _client(owner).get(f"/api/checkout/sessions/{session.id}/")
    attacker_response = _client(attacker).get(f"/api/checkout/sessions/{session.id}/")

    assert owner_response.status_code == 200
    owner_payload = assert_response_excludes_categories(
        owner_response,
        categories=(AUTH_KEY_MARKERS, STORAGE_KEY_MARKERS, INTERNAL_DEBUG_KEY_MARKERS),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"private-booking-pk", owner.email},
        allowed_keys={"id"},
    )
    assert set(owner_payload).issubset({"id", "status", "amount"})

    assert attacker_response.status_code == 404
    assert_response_excludes_categories(
        attacker_response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values={str(session.id), "500.00", "private-booking-pk", owner.email},
    )


@pytest.mark.django_db
def test_fake_provider_stk_response_is_minimal_and_does_not_expose_phone_or_daraja_identifiers(settings):
    settings.PAYMENT_PROVIDER_MODE = "fake"
    customer = _user("phase-3c-stk@example.com", "+254700300004")
    session = create_checkout_session(
        customer,
        Decimal("500.00"),
        "KES",
        "Private checkout",
        "booking",
        "private-booking-pk",
        "phase-3c-stk-session",
    )

    response = _client(customer).post(
        f"/api/checkout/sessions/{session.id}/mpesa/stk/",
        {"phone_number": customer.phone_number, "idempotency_key": "phase-3c-stk-attempt"},
        format="json",
    )

    assert response.status_code == 202
    payload = assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values={customer.phone_number, "fake_ws_CO", "fake_merchant"},
        allowed_keys={"attempt_id"},
    )
    assert set(payload).issubset({"attempt_id", "status"})


@pytest.mark.django_db
def test_webhook_response_does_not_echo_provider_payload_or_identifiers(settings):
    settings.CHECKOUT_ALLOWED_MPESA_IPS = ["127.0.0.1"]
    payload = {
        "CheckoutRequestID": "ws_CO_hidden_identifier",
        "MerchantRequestID": "merchant_hidden_identifier",
        "ResultCode": 1032,
        "Amount": "100.00",
        "MpesaReceiptNumber": "receipt_hidden_identifier",
    }

    response = APIClient().post(
        "/api/checkout/mpesa/webhook/",
        payload,
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )

    assert response.status_code == 202
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values={
            "ws_CO_hidden_identifier",
            "merchant_hidden_identifier",
            "receipt_hidden_identifier",
        },
    )
    assert LedgerTransaction.objects.count() == 0


@pytest.mark.django_db
def test_disabled_legacy_billing_routes_are_minimal_and_non_reflective(settings):
    settings.SAFARICOM_ALLOWED_IPS = ["127.0.0.1"]
    client = APIClient()
    stk = client.post(
        "/api/billing/stk-push/",
        {
            "checkout_request_id": "legacy-hidden-checkout",
            "ledger_id": "legacy-hidden-ledger",
            "phone": "+254712345678",
        },
        format="json",
        secure=True,
    )
    webhook = client.post(
        "/api/billing/mpesa-webhook/",
        {
            "checkout_request_id": "legacy-hidden-checkout",
            "ledger_id": "legacy-hidden-ledger",
            "phone": "+254712345678",
        },
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )

    assert stk.status_code == 410
    assert webhook.status_code == 410
    for response in (stk, webhook):
        assert_response_excludes_categories(
            response,
            categories=(
                AUTH_KEY_MARKERS,
                PAYMENT_PROVIDER_KEY_MARKERS,
                STORAGE_KEY_MARKERS,
                INTERNAL_DEBUG_KEY_MARKERS,
            ),
            forbidden_values=KNOWN_TEST_PII_VALUES | {"legacy-hidden-checkout", "legacy-hidden-ledger"},
        )
    assert LedgerTransaction.objects.count() == 0
