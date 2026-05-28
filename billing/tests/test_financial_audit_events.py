from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import FinancialAuditEvent, LedgerTransaction
from billing.services import (
    create_pending_ledger_transaction,
    mark_ledger_success,
    record_reversal,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_audit_event_created_on_financial_transition_and_payload_is_redacted():
    customer = User.objects.create_user(
        email="audit@beauty.com", phone_number="+254712100003"
    )
    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("1300.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "ws_CO_AUDIT_001",
    )

    mark_ledger_success(
        ledger.id,
        provider_receipt="QAUDIT001",
        raw_payload={"PhoneNumber": "+254712100003", "MpesaReceiptNumber": "QAUDIT001"},
        correlation_id="audit-correlation-001",
    )

    event = FinancialAuditEvent.objects.get(
        ledger_transaction=ledger, event_type="LEDGER_SUCCESS"
    )
    assert event.payload_hash
    assert event.correlation_id == "audit-correlation-001"
    assert "+254712100003" not in str(event.redacted_payload)
    assert "QAUDIT001" not in str(event.redacted_payload)


@pytest.mark.django_db(transaction=True)
def test_correction_workflow_creates_audit_event():
    customer = User.objects.create_user(
        email="correction@beauty.com", phone_number="+254712100004"
    )
    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("1300.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "ws_CO_AUDIT_002",
    )
    ledger = mark_ledger_success(ledger.id, provider_receipt="QAUDIT002")

    record_reversal(
        ledger.id,
        reason="provider chargeback",
        correlation_id="reversal-correlation-001",
    )

    assert FinancialAuditEvent.objects.filter(
        ledger_transaction=ledger,
        event_type="LEDGER_REVERSED",
        correlation_id="reversal-correlation-001",
    ).exists()
