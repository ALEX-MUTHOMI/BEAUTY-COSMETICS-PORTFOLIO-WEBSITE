from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction, SettlementRecord
from checkout.models import MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_duplicate_callback_contract_creates_single_ledger_and_settlement():
    customer = User.objects.create_user(email="dup-contract@aesthetic-os.test", phone_number="+254712640003")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Duplicate contract",
        "booking_candidate",
        "dup-contract",
        "dup-contract-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "dup-contract-stk")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "100.00",
        "MpesaReceiptNumber": "QDUPCONTRACT",
    }

    for _ in range(100):
        process_mpesa_callback(payload, remote_addr="127.0.0.1")

    assert LedgerTransaction.objects.count() == 1
    assert SettlementRecord.objects.count() == 1
    assert MpesaWebhookInbox.objects.count() == 1
