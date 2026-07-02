from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_reconciliation_report_includes_ledger_and_audit_counts(capsys):
    customer = User.objects.create_user(email="recon-ledger@aesthetic-os.test", phone_number="+254712750002")
    record_successful_checkout_payment(
        customer=customer,
        checkout_session_id="recon-ledger-session",
        amount=Decimal("190.00"),
        currency="KES",
        provider_reference="ws_CO_RECON_LEDGER",
        provider_receipt="QRECONLEDGER001",
        raw_payload={"CheckoutRequestID": "ws_CO_RECON_LEDGER"},
        correlation_id="recon-ledger-correlation",
    )

    call_command("payment_reconciliation_report")
    output = capsys.readouterr().out

    assert '"successful_ledgers": 1' in output
    assert '"audit_events": 2' in output
    assert "ws_CO_RECON_LEDGER" not in output
    assert "QRECONLEDGER001" not in output
