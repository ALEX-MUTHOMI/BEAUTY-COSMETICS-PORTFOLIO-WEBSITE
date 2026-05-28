import base64
import json
from decimal import Decimal

import pytest

from checkout.providers.base import ProviderUnavailable
from checkout.providers.mpesa import MpesaProvider


def _configure_sandbox(monkeypatch):
    monkeypatch.setenv("DARAJA_ENV", "sandbox")
    monkeypatch.setenv("DARAJA_CONSUMER_KEY", "consumer-key-test")
    monkeypatch.setenv("DARAJA_CONSUMER_SECRET", "consumer-secret-test")
    monkeypatch.setenv("DARAJA_SHORTCODE", "174379")
    monkeypatch.setenv("DARAJA_PASSKEY", "passkey-test")
    monkeypatch.setenv("DARAJA_CALLBACK_URL", "https://callback.example.test/mpesa/")
    monkeypatch.setenv("DARAJA_ACCOUNT_REFERENCE", "BEAUTYTEST")
    monkeypatch.setenv("DARAJA_TRANSACTION_DESC", "Beauty SaaS test")
    monkeypatch.setenv("DARAJA_TEST_MSISDN", "254712345678")


def test_real_daraja_adapter_builds_official_stk_payload(monkeypatch, caplog):
    _configure_sandbox(monkeypatch)
    provider = MpesaProvider()

    payload = provider.build_stk_push_payload(
        phone_number="254712345678",
        amount=Decimal("10.00"),
        account_reference="BEAUTYTEST",
        description="Beauty SaaS test",
        callback_url="https://callback.example.test/mpesa/",
    )

    assert payload["BusinessShortCode"] == "174379"
    assert (
        payload["Password"]
        == base64.b64encode(
            f"174379passkey-test{payload['Timestamp']}".encode()
        ).decode()
    )
    assert payload["Timestamp"].isdigit()
    assert payload["TransactionType"] == "CustomerPayBillOnline"
    assert payload["Amount"] == 10
    assert payload["PartyA"] == "254712345678"
    assert payload["PartyB"] == "174379"
    assert payload["PhoneNumber"] == "254712345678"
    assert payload["CallBackURL"] == "https://callback.example.test/mpesa/"
    assert payload["AccountReference"] == "BEAUTYTEST"
    assert payload["TransactionDesc"] == "Beauty SaaS test"
    assert "254712345678" not in caplog.text
    assert "passkey-test" not in caplog.text


def test_oauth_token_retrieval_uses_basic_auth_and_redacts_token(monkeypatch, caplog):
    _configure_sandbox(monkeypatch)
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps(
                {"access_token": "sandbox-token-secret", "expires_in": "3599"}
            ).encode()

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
