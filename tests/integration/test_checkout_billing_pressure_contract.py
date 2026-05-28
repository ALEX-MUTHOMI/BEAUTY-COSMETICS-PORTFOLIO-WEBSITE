from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections

from billing.models import LedgerTransaction, SettlementRecord
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_checkout_billing_contract_under_many_valid_callbacks():
    customer = User.objects.create_user(
        email="contract-pressure@beauty.com", phone_number="+254712640001"
    )
    payloads = []
    for index in range(100):
        session = create_checkout_session(
            customer,
            Decimal("100.00"),
            "KES",
            "Contract pressure",
            "booking_candidate",
            f"contract-pressure-{index}",
            f"contract-pressure-idem-{index}",
        )
        attempt = initiate_mpesa_stk(
            session.id, customer.phone_number, f"contract-pressure-stk-{index}"
        )
        payloads.append(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "100.00",
                "MpesaReceiptNumber": f"QCONTRACT{index:04d}",
            }
        )

    def callback(payload):
        close_old_connections()
        try:
            return process_mpesa_callback(
                payload, remote_addr="127.0.0.1"
            ).session.status
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(callback, payload) for payload in payloads]
        statuses = [future.result(timeout=30) for future in as_completed(futures)]

    assert statuses.count("paid") == 100
    assert (
        LedgerTransaction.objects.filter(
            status=LedgerTransaction.Status.SUCCESS
        ).count()
        == 100
    )
    assert SettlementRecord.objects.count() == 100
