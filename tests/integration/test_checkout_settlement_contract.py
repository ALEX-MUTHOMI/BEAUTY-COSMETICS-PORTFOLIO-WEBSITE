from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction, SettlementRecord
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_successful_checkout_creates_pending_settlement_contract():
    customer = User.objects.create_user(email="settlement-contract@aesthetic-os.test", phone_number="+254712300005")
    session = create_checkout_session(
        customer,
        Decimal("2800.00"),
        "KES",
        "Settlement",
        "booking_candidate",
        "settlement-contract-001",
        "settlement-contract-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712300005", "settlement-contract-stk-001")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "2800.00",
            "MpesaReceiptNumber": "QSETTLECONTRACT001",
        },
        remote_addr="127.0.0.1",
    )

    ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))
    settlement = SettlementRecord.objects.get(ledger_transaction=ledger)
    assert settlement.settlement_status == SettlementRecord.Status.PENDING
    assert settlement.amount == Decimal("2800.00")
