import json

import pytest
from django.core.management import call_command

from checkout.models import MpesaWebhookInbox
from checkout.services import record_mpesa_webhook_event


@pytest.mark.django_db
def test_payment_reconciliation_report_redacts_webhook_payload(capsys):
    record_mpesa_webhook_event(
        {
            "CheckoutRequestID": "ws_CO_RECON_SECRET",
            "MerchantRequestID": "merchant_RECON_SECRET",
            "PhoneNumber": "+254712750001",
            "ResultCode": 0,
            "Amount": "180.00",
            "MpesaReceiptNumber": "QRECON001",
        },
        correlation_id="recon-correlation",
    )

    call_command(
        "payment_reconciliation_report", "--status", MpesaWebhookInbox.Status.RECEIVED
    )
    output = capsys.readouterr().out
    report = json.loads(output)

    assert report["counts"]["received"] == 1
    assert "ws_CO_RECON_SECRET" not in output
    assert "merchant_RECON_SECRET" not in output
    assert "+254712750001" not in output
    assert "QRECON001" not in output
