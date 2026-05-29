from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_record_successful_checkout_payment_creates_accounting_artifacts_without_raw_provider_ids():
    customer = User.objects.create_user(email="billing-service@beauty.com", phone_number="+254712500001")

    ledger, created = record_successful_checkout_payment(
        customer=customer,
        checkout_session_id="checkout-service-001",
        amount=Decimal("1500.00"),
        currency="KES",
        provider_reference="ws_CO_SERVICE_RAW",
        provider_receipt="QSERVICE001",
        raw_payload={
            "CheckoutRequestID": "ws_CO_SERVICE_RAW",
            "MpesaReceiptNumber": "QSERVICE001",
            "PhoneNumber": "+254712500001",
        },
        correlation_id="billing-service-correlation",
    )

    assert created is True
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert ledger.checkout_request_id is None
    assert ledger.provider_reference_hash
    assert ledger.provider_receipt_hash
    assert SettlementRecord.objects.filter(ledger_transaction=ledger).exists()
    assert FinancialAuditEvent.objects.filter(
        ledger_transaction=ledger,
        event_type="LEDGER_SUCCESS",
        correlation_id="billing-service-correlation",
    ).exists()
