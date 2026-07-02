import base64
import io
import json
import re
import urllib.error
from decimal import Decimal

import pytest

from checkout.exceptions import CheckoutValidationError
from checkout.providers.base import ProviderUnavailable
from checkout.providers.mpesa import MpesaProvider


def _configure_sandbox(monkeypatch):
    monkeypatch.setenv("DARAJA_ENV", "sandbox")
    monkeypatch.setenv("DARAJA_CONSUMER_KEY", "consumer-key-test")
    monkeypatch.setenv("DARAJA_CONSUMER_SECRET", "consumer-secret-test")
    monkeypatch.setenv("DARAJA_SHORTCODE", "174379")
    monkeypatch.setenv("DARAJA_PASSKEY", "passkey-test")
    monkeypatch.setenv("DARAJA_CALLBACK_URL", "https://callback.example.test/mpesa/")
    monkeypatch.setenv("DARAJA_ACCOUNT_REFERENCE", "AESTHETICOS")
    monkeypatch.setenv("DARAJA_TRANSACTION_DESC", "AestheticOS test")
    monkeypatch.setenv("DARAJA_TEST_MSISDN", "254712345678")


def test_real_daraja_adapter_builds_official_stk_payload(monkeypatch, caplog):
    _configure_sandbox(monkeypatch)
    provider = MpesaProvider()

    payload = provider.build_stk_push_payload(
        phone_number="254712345678",
        amount=Decimal("10.00"),
        account_reference="AESTHETICOS",
        description="AestheticOS test",
        callback_url="https://callback.example.test/mpesa/",
    )

    assert payload["BusinessShortCode"] == "174379"
    assert payload["Password"] == base64.b64encode(f"174379passkey-test{payload['Timestamp']}".encode()).decode()
    assert re.fullmatch(r"\d{14}", payload["Timestamp"])
    assert payload["TransactionType"] == "CustomerPayBillOnline"
    assert payload["Amount"] == 10
    assert payload["PartyA"] == "254712345678"
    assert payload["PartyB"] == "174379"
    assert payload["PhoneNumber"] == "254712345678"
    assert payload["CallBackURL"] == "https://callback.example.test/mpesa/"
    assert payload["AccountReference"] == "AESTHETICOS"
    assert payload["TransactionDesc"] == "AestheticOS test"
    assert "254712345678" not in caplog.text
    assert "passkey-test" not in caplog.text


def test_real_daraja_payload_callback_url_is_clean_https_and_matches_env_host(monkeypatch):
    _configure_sandbox(monkeypatch)
    monkeypatch.setenv(
        "DARAJA_CALLBACK_URL",
        "DARAJA_CALLBACK_URL=https://aesthetic-os-checkout.trycloudflare.com/api/checkout/mpesa/webhook/",
    )

    payload = MpesaProvider().build_stk_push_payload(
        phone_number="0712345678",
        amount=Decimal("10.99"),
        account_reference="AESTHETICTEST-LONG-REFERENCE",
        description="x" * 200,
        callback_url="DARAJA_CALLBACK_URL=https://aesthetic-os-checkout.trycloudflare.com/api/checkout/mpesa/webhook/",
    )

    assert payload["CallBackURL"] == "https://aesthetic-os-checkout.trycloudflare.com/api/checkout/mpesa/webhook/"
    assert payload["PartyA"] == "254712345678"
    assert payload["PhoneNumber"] == "254712345678"
    assert payload["Amount"] == 10
    assert len(payload["AccountReference"]) <= 12
    assert len(payload["TransactionDesc"]) <= 100


def test_real_daraja_payload_rejects_malformed_callback_url(monkeypatch):
    _configure_sandbox(monkeypatch)

    with pytest.raises(ProviderUnavailable, match="callback URL"):
        MpesaProvider().build_stk_push_payload(
            phone_number="254712345678",
            amount=Decimal("10.00"),
            account_reference="AESTHETICOS",
            description="AestheticOS test",
            callback_url="http://localhost:8000/api/checkout/mpesa/webhook/",
        )


def test_real_daraja_payload_rejects_callback_host_mismatch(monkeypatch):
    _configure_sandbox(monkeypatch)

    with pytest.raises(ProviderUnavailable, match="host"):
        MpesaProvider().build_stk_push_payload(
            phone_number="254712345678",
            amount=Decimal("10.00"),
            account_reference="AESTHETICOS",
            description="AestheticOS test",
            callback_url="https://attacker.example.test/api/checkout/mpesa/webhook/",
        )


def test_real_daraja_payload_rejects_invalid_phone_amount_shortcode_and_passkey(monkeypatch):
    _configure_sandbox(monkeypatch)
    provider = MpesaProvider()

    with pytest.raises(CheckoutValidationError):
        provider.build_stk_push_payload(
            "not-a-phone", Decimal("10.00"), "AESTHETICOS", "desc", "https://callback.example.test/mpesa/"
        )

    with pytest.raises(ProviderUnavailable, match="amount"):
        provider.build_stk_push_payload(
            "254712345678", Decimal("0.00"), "AESTHETICOS", "desc", "https://callback.example.test/mpesa/"
        )

    monkeypatch.setenv("DARAJA_SHORTCODE", "shortcode")
    with pytest.raises(ProviderUnavailable, match="SHORTCODE"):
        provider.build_stk_push_payload(
            "254712345678", Decimal("10.00"), "AESTHETICOS", "desc", "https://callback.example.test/mpesa/"
        )

    monkeypatch.setenv("DARAJA_SHORTCODE", "174379")
    monkeypatch.setenv("DARAJA_PASSKEY", "short")
    with pytest.raises(ProviderUnavailable, match="PASSKEY"):
        provider.build_stk_push_payload(
            "254712345678", Decimal("10.00"), "AESTHETICOS", "desc", "https://callback.example.test/mpesa/"
        )


def test_oauth_token_retrieval_uses_basic_auth_and_redacts_token(monkeypatch, caplog):
    _configure_sandbox(monkeypatch)
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps({"access_token": "sandbox-token-secret", "expires_in": "3599"}).encode()

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["auth"] = request.headers["Authorization"]
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = MpesaProvider(connect_timeout=1, read_timeout=2)

    token = provider.retrieve_oauth_token()

    assert token == "sandbox-token-secret"
    assert captured["url"].endswith("/oauth/v1/generate?grant_type=client_credentials")
    assert captured["auth"].startswith("Basic ")
    assert captured["timeout"] == 3
    assert "sandbox-token-secret" not in caplog.text
    assert "consumer-secret-test" not in caplog.text


def test_oauth_error_returns_controlled_provider_error(monkeypatch):
    _configure_sandbox(monkeypatch)

    def fake_urlopen(request, timeout):
        raise TimeoutError("socket timed out")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(ProviderUnavailable):
        MpesaProvider(connect_timeout=1, read_timeout=1).retrieve_oauth_token()


def test_stk_http_400_body_is_normalized_into_safe_redacted_diagnostic(monkeypatch):
    _configure_sandbox(monkeypatch)

    def fake_urlopen(request, timeout):
        body = json.dumps(
            {
                "errorCode": "400.002.02",
                "errorMessage": "Bad request for 254712345678 with password passkey-test",
                "requestId": "raw-provider-request-id",
                "CheckoutRequestID": "ws_CO_SECRET",
                "MerchantRequestID": "merchant-secret",
            }
        ).encode()
        raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {}, io.BytesIO(body))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = MpesaProvider()
    monkeypatch.setattr(provider, "retrieve_oauth_token", lambda: "raw-token-secret")

    with pytest.raises(ProviderUnavailable) as exc:
        provider.initiate_stk_push(
            phone_number="254712345678",
            amount=Decimal("10.00"),
            account_reference="AESTHETICOS",
            description="AestheticOS test",
            callback_url="https://callback.example.test/mpesa/",
            idempotency_key="idem",
        )

    message = str(exc.value)
    assert "400" in message
    assert "400.002.02" in message
    assert "254712345678" not in message
    assert "passkey-test" not in message
    assert "raw-token-secret" not in message
    assert "raw-provider-request-id" not in message
    assert "ws_CO_SECRET" not in message
    assert "merchant-secret" not in message
