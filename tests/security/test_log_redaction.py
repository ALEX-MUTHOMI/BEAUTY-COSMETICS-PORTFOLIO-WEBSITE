from billing.redaction import redact_financial_payload
from checkout.redaction import redact_checkout_payload


def test_payment_redaction_prevents_raw_sensitive_values_in_logs():
    payload = {
        "PhoneNumber": "+254712400005",
        "MpesaReceiptNumber": "QLOGRAW001",
        "CheckoutRequestID": "ws_CO_LOG_RAW",
        "access_token": "secret-token",
    }

    redacted_payload = redact_checkout_payload(redact_financial_payload(payload))
    rendered = str(redacted_payload)

    assert "+254712400005" not in rendered
    assert "QLOGRAW001" not in rendered
    assert "ws_CO_LOG_RAW" not in rendered
    assert "secret-token" not in rendered
