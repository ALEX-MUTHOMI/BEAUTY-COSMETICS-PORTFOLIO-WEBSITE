import pytest
from django.test import Client
from rest_framework.test import APIClient

from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    INTERNAL_DEBUG_KEY_MARKERS,
    KNOWN_TEST_PII_VALUES,
    PAYMENT_PROVIDER_KEY_MARKERS,
    STORAGE_KEY_MARKERS,
    assert_response_excludes_categories,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "path", "expected_status"),
    [
        ("get", "/api/bookings/status/not-a-valid-token/", 404),
        ("get", "/api/staff/bookings/not-a-valid-token/", 403),
        ("get", "/api/legal/documents/%3Cscript%3Ealert(1)%3C%2Fscript%3E/", 404),
        ("get", "/api/unknown-sensitive-route/", 404),
    ],
)
def test_common_denial_responses_do_not_expose_sensitive_fields(method, path, expected_status):
    client = Client()
    response = getattr(client, method)(path, secure=True)

    assert response.status_code == expected_status
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"not-a-valid-token", "<script>", "alert(1)"},
    )


@pytest.mark.django_db
def test_malformed_json_booking_hold_error_is_non_leaky():
    response = Client().post(
        "/api/bookings/holds/",
        data='{"customer": {"email": "grace@example.com"',
        content_type="application/json",
        secure=True,
    )

    assert response.status_code in {400, 403}
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES,
    )


@pytest.mark.django_db
def test_malformed_webhook_error_is_non_leaky_and_does_not_echo_payload(settings):
    settings.CHECKOUT_ALLOWED_MPESA_IPS = ["127.0.0.1"]
    response = APIClient().post(
        "/api/checkout/mpesa/webhook/",
        {
            "CheckoutRequestID": "malformed-hidden-checkout",
            "MerchantRequestID": "malformed-hidden-merchant",
            "phone": "+254712345678",
        },
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )

    assert response.status_code == 400
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"malformed-hidden-checkout", "malformed-hidden-merchant"},
    )


@pytest.mark.django_db
def test_unsupported_method_response_does_not_include_debug_or_payload_values():
    response = Client().put(
        "/api/bookings/status/not-a-valid-token/",
        data='{"token": "attacker-token", "email": "grace@example.com"}',
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 405
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES | {"attacker-token", "not-a-valid-token"},
    )
