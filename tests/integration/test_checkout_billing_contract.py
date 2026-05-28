from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from checkout.models import CheckoutSession
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_checkout_success_creates_single_ledger_audit_and_settlement():
    customer = User.objects.create_user(
        email="contract-success@beauty.com", phone_number="+254712300001"
    )
    session = create_checkout_session(
        customer,
        Decimal("2600.00"),
        "KES",
        "Contract",
        "booking_candidate",
        "contract-001",
        "contract-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712300001", "contract-stk-001")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "2600.00",
            "MpesaReceiptNumber": "QCONTRACT001",
        },
        remote_addr="127.0.0.1",
    )
    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "2600.00",
            "MpesaReceiptNumber": "QCONTRACT001",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))
    assert session.status == CheckoutSession.Status.PAID
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 1
    )
    assert FinancialAuditEvent.objects.filter(
        ledger_transaction=ledger, event_type="LEDGER_SUCCESS"
    ).exists()
    assert SettlementRecord.objects.filter(ledger_transaction=ledger).exists()
