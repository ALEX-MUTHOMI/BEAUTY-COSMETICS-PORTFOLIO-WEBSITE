from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import FinancialAuditEvent, LedgerTransaction
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_ledger_and_audit_timestamps_are_timezone_aware():
    customer = User.objects.create_user(email="billing-tz@beauty.com", phone_number="+254712710001")

    ledger, created = record_successful_checkout_payment(
        customer=customer,
        checkout_session_id="billing-tz-session",
        amount=Decimal("75.00"),
        currency="KES",
        provider_reference="ws_CO_BILLING_TZ",
        provider_receipt="QBTZ001",
        raw_payload={"CheckoutRequestID": "ws_CO_BILLING_TZ"},
        correlation_id="tz-correlation",
    )

    audit = FinancialAuditEvent.objects.get(
        ledger_transaction=ledger,
        event_type="LEDGER_SUCCESS",
    )
    assert created is True
    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert timezone.is_aware(ledger.created_at)
    assert timezone.is_aware(ledger.credited_at)
    assert timezone.is_aware(audit.created_at)
