import pytest

from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    PAYMENT_PROVIDER_KEY_MARKERS,
    assert_no_forbidden_keys,
)


def test_sensitive_field_helper_reports_key_category_without_value_leakage():
    payload = {
        "checkout_request_id": "raw-provider-id-that-must-not-appear-in-failure-output",
        "nested": {"password_hash": "hash-that-must-not-appear-in-failure-output"},
    }

    with pytest.raises(AssertionError) as exc:
        assert_no_forbidden_keys(payload, AUTH_KEY_MARKERS | PAYMENT_PROVIDER_KEY_MARKERS)

    rendered = str(exc.value)
    assert "checkout_request_id" in rendered
    assert "password" in rendered
    assert "raw-provider-id-that-must-not-appear" not in rendered
    assert "hash-that-must-not-appear" not in rendered


def test_sensitive_field_helper_supports_route_specific_allowed_public_keys():
    payload = {"checkout_public_id": "opaque-owner-scoped-id", "status": "payment_pending"}

    assert_no_forbidden_keys(payload, {"checkout"}, allowed_keys={"checkout_public_id"})
