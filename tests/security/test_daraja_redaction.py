import logging

from checkout.redaction import redact_checkout_payload


def test_daraja_sensitive_values_are_redacted_from_logs(caplog):
    payload = {
        "PhoneNumber": "254712345678",
        "CheckoutRequestID": "ws_CO_SECRET_123",
        "MerchantRequestID": "merchant_SECRET_123",
        "MpesaReceiptNumber": "QSECRET001",
        "access_token": "token-secret-value",
        "consumer_secret": "consumer-secret-value",
        "passkey": "passkey-secret-value",
    }

    with caplog.at_level(logging.INFO):
        logging.getLogger("checkout.daraja").info("daraja=%s", redact_checkout_payload(payload))

    assert "254712345678" not in caplog.text
    assert "ws_CO_SECRET_123" not in caplog.text
    assert "merchant_SECRET_123" not in caplog.text
    assert "QSECRET001" not in caplog.text
    assert "token-secret-value" not in caplog.text
    assert "consumer-secret-value" not in caplog.text
    assert "passkey-secret-value" not in caplog.text
