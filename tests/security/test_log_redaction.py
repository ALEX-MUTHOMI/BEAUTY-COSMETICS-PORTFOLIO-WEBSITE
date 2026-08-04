import logging

from billing.redaction import redact_financial_payload
from checkout.redaction import redact_checkout_payload


def test_payment_redaction_prevents_raw_sensitive_values_in_logs(caplog):
    payload = {
        "PhoneNumber": "+254712400005",
        "MpesaReceiptNumber": "QLOGRAW001",
        "CheckoutRequestID": "ws_CO_LOG_RAW",
        "access_token": "secret-token",
    }

    with caplog.at_level(logging.INFO):
        redacted_payload = redact_checkout_payload(redact_financial_payload(payload))
        logging.getLogger("payment-redaction-test").info("payload=%s", redacted_payload)

    output = caplog.text
    assert "+254712400005" not in output
    assert "QLOGRAW001" not in output
    assert "ws_CO_LOG_RAW" not in output
    assert "secret-token" not in output
