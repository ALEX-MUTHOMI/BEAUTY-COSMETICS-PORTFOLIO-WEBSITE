from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction, SettlementRecord
from billing.services import create_pending_ledger_transaction, mark_ledger_success

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_successful_credit_creates_pending_settlement_record():
    customer = User.objects.create_user(email="settlement@beauty.com", phone_number="+254712100005")
    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("2200.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "ws_CO_SETTLEMENT_001",
    )

    mark_ledger_success(ledger.id, provider_receipt="QSETTLE001")

    settlement = SettlementRecord.objects.get(ledger_transaction=ledger)
    assert settlement.settlement_status == SettlementRecord.Status.PENDING
    assert settlement.amount == Decimal("2200.00")
    assert settlement.currency == "KES"
    assert settlement.settled_at is None
