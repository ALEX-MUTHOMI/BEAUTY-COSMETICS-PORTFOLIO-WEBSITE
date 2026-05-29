import json
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingInvariantError
from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from checkout.providers.mpesa import MpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk, process_mpesa_callback

User = get_user_model()
FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "daraja"


def _success_event():
    payload = json.loads((FIXTURE_DIR / "stk_success_callback.json").read_text())
    return MpesaProvider().normalize_callback(payload)


@pytest.mark.django_db(transaction=True)
def test_daraja_success_creates_one_immutable_ledger_audit_and_settlement():
    customer = User.objects.create_user(email="billing-daraja-shape@beauty.com", phone_number="+254712770002")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Billing Daraja shape",
        "booking_candidate",
        "billing-daraja-shape",
        "billing-daraja-shape-session",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "billing-daraja-shape-stk")
    event = _success_event()
    attempt.provider_request_id = event["CheckoutRequestID"]
    attempt.merchant_request_id = event["MerchantRequestID"]
    attempt.save(update_fields=["provider_request_id", "merchant_request_id", "updated_at"])

    process_mpesa_callback(event, remote_addr="127.0.0.1")
    process_mpesa_callback(event, remote_addr="127.0.0.1")
    ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))

    assert ledger.status == LedgerTransaction.Status.SUCCESS
    assert FinancialAuditEvent.objects.filter(ledger_transaction=ledger, event_type="LEDGER_SUCCESS").count() == 1
    assert SettlementRecord.objects.filter(ledger_transaction=ledger).count() == 1

    ledger.amount = Decimal("999.00")
    with pytest.raises(BillingInvariantError):
        ledger.save()
