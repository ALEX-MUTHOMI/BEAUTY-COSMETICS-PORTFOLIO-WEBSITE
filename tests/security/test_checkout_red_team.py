from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.exceptions import CheckoutStateError, CheckoutValidationError
from checkout.services import (
    cancel_checkout_session,
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)
from users.services import get_redis_client

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_red_team_checkout_attack_vectors_are_blocked(settings):
    customer = User.objects.create_user(email="checkout-redteam@aesthetic-os.test", phone_number="+254712400001")
    session = create_checkout_session(
        customer,
        Decimal("1900.00"),
        "KES",
        "Red team",
        "booking_candidate",
        "redteam-001",
        "redteam-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712400001", "redteam-stk-001")

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "1.00",
                "MpesaReceiptNumber": "QBADAMOUNT001",
            },
            remote_addr="127.0.0.1",
        )

    cancel_checkout_session(session.id)
    with pytest.raises(CheckoutStateError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "1900.00",
                "MpesaReceiptNumber": "QCANCELLED001",
            },
            remote_addr="127.0.0.1",
        )

    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    settings.TRUSTED_PROXY_CIDRS = []
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"CheckoutRequestID": "ws_CO_SPOOF", "ResultCode": 0},
        format="json",
        REMOTE_ADDR="203.0.113.200",
        HTTP_X_FORWARDED_FOR="196.201.214.10",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(transaction=True)
def test_red_team_bruteforce_stk_push_attempts_are_throttled():
    customer = User.objects.create_user(email="checkout-bruteforce@aesthetic-os.test", phone_number="+254712400002")
    session = create_checkout_session(
        customer,
        Decimal("1900.00"),
        "KES",
        "Bruteforce",
        "booking_candidate",
        "bruteforce-001",
        "bruteforce-idem-001",
    )
    redis_client = get_redis_client()
    for key in redis_client.scan_iter("throttle:*"):
        redis_client.delete(key)

    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    client.force_authenticate(user=customer)
    statuses = [
        client.post(
            f"/api/checkout/sessions/{session.id}/mpesa/stk/",
            {"phone_number": "+254712400002", "idempotency_key": f"bruteforce-{index}"},
            format="json",
            REMOTE_ADDR="198.51.100.77",
        ).status_code
        for index in range(6)
    ]

    assert statuses.count(status.HTTP_202_ACCEPTED) == 3
    assert statuses.count(status.HTTP_429_TOO_MANY_REQUESTS) == 3
