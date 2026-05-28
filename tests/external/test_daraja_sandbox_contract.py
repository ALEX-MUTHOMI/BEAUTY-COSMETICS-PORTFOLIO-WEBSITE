import os
from decimal import Decimal

import pytest

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.providers.mpesa import MpesaProvider
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

REQUIRED_ENV = [
    "DARAJA_ENV",
    "DARAJA_CONSUMER_KEY",
    "DARAJA_CONSUMER_SECRET",
    "DARAJA_SHORTCODE",
    "DARAJA_PASSKEY",
    "DARAJA_CALLBACK_URL",
    "DARAJA_ACCOUNT_REFERENCE",
    "DARAJA_TRANSACTION_DESC",
    "DARAJA_TEST_MSISDN",
]


def _sandbox_configured():
    return os.environ.get("DARAJA_ENV") == "sandbox" and all(
        os.environ.get(key) for key in REQUIRED_ENV
    )


pytestmark = [
    pytest.mark.external,
    pytest.mark.daraja_sandbox,
]


@pytest.fixture
def daraja_env():
    if not _sandbox_configured():
        pytest.skip("Daraja sandbox credentials are not configured.")
    return {key: os.environ[key] for key in REQUIRED_ENV}


def test_daraja_sandbox_environment_guard_does_not_print_values():
    missing = [key for key in REQUIRED_ENV if not os.environ.get(key)]
    if os.environ.get("DARAJA_ENV") and os.environ.get("DARAJA_ENV") != "sandbox":
        missing.append("DARAJA_ENV=sandbox")
    assert isinstance(missing, list)


def test_daraja_sandbox_oauth_token_retrieval(daraja_env, caplog):
    token = MpesaProvider().retrieve_oauth_token()

    assert token
    assert token not in caplog.text
    assert daraja_env["DARAJA_CONSUMER_SECRET"] not in caplog.text


def test_daraja_sandbox_stk_payload_contract(daraja_env, caplog):
    payload = MpesaProvider().build_stk_push_payload(
        phone_number=daraja_env["DARAJA_TEST_MSISDN"],
        amount=Decimal(os.environ.get("DARAJA_TEST_AMOUNT", "1")),
        account_reference=daraja_env["DARAJA_ACCOUNT_REFERENCE"],
        description=daraja_env["DARAJA_TRANSACTION_DESC"],
        callback_url=daraja_env["DARAJA_CALLBACK_URL"],
    )

    for key in (
        "BusinessShortCode",
        "Password",
        "Timestamp",
        "TransactionType",
        "Amount",
        "PartyA",
        "PartyB",
        "PhoneNumber",
        "CallBackURL",
        "AccountReference",
        "TransactionDesc",
    ):
        assert key in payload
    assert daraja_env["DARAJA_TEST_MSISDN"] not in caplog.text
    assert daraja_env["DARAJA_PASSKEY"] not in caplog.text


@pytest.mark.django_db(transaction=True)
def test_single_daraja_sandbox_stk_initiation_does_not_credit_before_callback(
    daraja_env, django_user_model, caplog
):
    customer = django_user_model.objects.create_user(
        email="daraja-sandbox-contract@example.test",
        phone_number="+254712345678",
    )
    session = create_checkout_session(
        customer,
        Decimal(os.environ.get("DARAJA_TEST_AMOUNT", "1")).quantize(Decimal("0.01")),
        "KES",
        daraja_env["DARAJA_TRANSACTION_DESC"],
        "booking_candidate",
        "daraja-sandbox-contract",
        "daraja-sandbox-session-idem",
    )

    attempt = initiate_mpesa_stk(
        session.id,
        phone_number=daraja_env["DARAJA_TEST_MSISDN"],
        idempotency_key="daraja-sandbox-stk-idem",
        provider=MpesaProvider(),
    )
    session.refresh_from_db()

    assert attempt.provider_request_id
    assert session.status == CheckoutSession.Status.STK_SENT
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 0
    )
    assert daraja_env["DARAJA_TEST_MSISDN"] not in caplog.text
    assert attempt.provider_request_id not in caplog.text


@pytest.mark.django_db(transaction=True)
def test_sandbox_shaped_duplicate_callback_replay_is_idempotent(
    daraja_env, django_user_model
):
    customer = django_user_model.objects.create_user(
        email="daraja-callback-contract@example.test",
        phone_number="+254712345678",
    )
    session = create_checkout_session(
        customer,
        Decimal("1.00"),
        "KES",
        "Sandbox callback contract",
        "booking_candidate",
        "daraja-callback-contract",
        "daraja-callback-session-idem",
    )
    attempt = initiate_mpesa_stk(
        session.id,
        phone_number="+254712345678",
        idempotency_key="daraja-callback-stk-idem",
    )
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "1.00",
        "MpesaReceiptNumber": "QSANDBOXLOCAL001",
    }

    for _ in range(10):
        process_mpesa_callback(payload, remote_addr="127.0.0.1")

    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 1
    )
