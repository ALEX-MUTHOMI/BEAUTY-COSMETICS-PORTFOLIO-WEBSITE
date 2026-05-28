import pytest
from django.core.management import call_command

from checkout.services import record_mpesa_webhook_event


@pytest.mark.django_db
def test_reconciliation_report_does_not_expose_sensitive_payloads(capsys):
    record_mpesa_webhook_event(
        {
            "CheckoutRequestID": "ws_CO_RECON_ATTACK",
            "MerchantRequestID": "merchant_RECON_ATTACK",
            "PhoneNumber": "+254712750003",
            "access_token": "token-recon-secret",
            "ResultCode": 1,
        }
    )

    call_command("payment_reconciliation_report", "--include-events")
    output = capsys.readouterr().out

    assert "ws_CO_RECON_ATTACK" not in output
    assert "merchant_RECON_ATTACK" not in output
    assert "+254712750003" not in output
    assert "token-recon-secret" not in output
