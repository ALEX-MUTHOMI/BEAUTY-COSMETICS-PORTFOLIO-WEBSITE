from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework import status
from rest_framework.test import APIClient

from billing.models import LedgerTransaction, SettlementRecord
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)
from users.services import OTPService, get_redis_client

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_redis_tokens():
    client = get_redis_client()
    for key in client.scan_iter("throttle:*"):
        client.delete(key)
    for key in client.scan_iter("otp:*"):
        client.delete(key)


def secure_client(user=None):
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    if user is not None:
        client.force_authenticate(user=user)
    return client


def create_stk_checkout(customer, amount=Decimal("2400.00")):
    session = create_checkout_session(
        customer,
        amount,
        "KES",
        "Chaos checkout",
        "booking_candidate",
        "chaos-purchasable-001",
        "chaos-session-idem-001",
    )
    attempt = initiate_mpesa_stk(
        session.id, customer.phone_number, "chaos-stk-idem-001"
    )
    return session, attempt


@pytest.mark.django_db(transaction=True)
def test_parallel_mpesa_callbacks_credit_checkout_once():
    customer = User.objects.create_user(
        email="chaos-callback@beauty.com", phone_number="+254712345679"
    )
    session, attempt = create_stk_checkout(customer)
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "2400.00",
        "MpesaReceiptNumber": "QCHAOS001",
    }

    def callback():
        close_old_connections()
        try:
            return process_mpesa_callback(
                payload, remote_addr="127.0.0.1"
            ).inbox.processing_status
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(callback) for _ in range(10)]
        statuses = [future.result(timeout=15) for future in as_completed(futures)]

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.PAID
    assert statuses.count(MpesaWebhookInbox.Status.PROCESSED) == 1
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )
    assert (
        SettlementRecord.objects.filter(
            ledger_transaction__external_correlation_id=str(session.id)
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_auth_otp_and_checkout_callback_do_not_deadlock():
    customer = User.objects.create_user(
        email="chaos-auth@beauty.com", phone_number="+254712345680"
    )
    session, attempt = create_stk_checkout(customer, Decimal("750.00"))
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "750.00",
        "MpesaReceiptNumber": "QCHAOSOTP001",
    }

    def checkout_path():
        close_old_connections()
        try:
            return process_mpesa_callback(
                payload, remote_addr="127.0.0.1"
            ).session.status
        finally:
            close_old_connections()

    def auth_path():
        close_old_connections()
        try:
            otp = OTPService.generate_otp(customer.email)
            return OTPService.verify_otp(customer.email, otp)
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(checkout_path), executor.submit(auth_path)]
        results = [future.result(timeout=15) for future in as_completed(futures)]

    assert CheckoutSession.Status.PAID in results
    assert True in results


@pytest.mark.django_db(transaction=True)
def test_checkout_webhook_rejects_x_forwarded_for_spoofing(settings):
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    settings.TRUSTED_PROXY_CIDRS = []
    response = secure_client().post(
        "/api/checkout/mpesa/webhook/",
        {"CheckoutRequestID": "ws_CO_SPOOF", "ResultCode": 0, "Amount": "500.00"},
        format="json",
        REMOTE_ADDR="203.0.113.99",
        HTTP_X_FORWARDED_FOR="196.201.214.10",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert LedgerTransaction.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_checkout_stk_token_bucket_blocks_fourth_burst_request():
    customer = User.objects.create_user(
        email="chaos-throttle@beauty.com", phone_number="+254712345681"
    )
    session = create_checkout_session(
        customer,
        Decimal("1200.00"),
        "KES",
        "Throttle checkout",
        "booking_candidate",
        "chaos-throttle-001",
        "chaos-throttle-session",
    )
    client = secure_client(customer)

    statuses = []
    for index in range(4):
        response = client.post(
            f"/api/checkout/sessions/{session.id}/mpesa/stk/",
            {
                "phone_number": customer.phone_number,
                "idempotency_key": f"chaos-throttle-stk-{index}",
            },
            format="json",
            REMOTE_ADDR="198.51.100.55",
        )
        statuses.append(response.status_code)

    assert statuses[:3] == [status.HTTP_202_ACCEPTED] * 3
    assert statuses[3] == status.HTTP_429_TOO_MANY_REQUESTS
