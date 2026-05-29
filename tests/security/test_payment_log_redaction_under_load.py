import logging

from checkout.redaction import redact_checkout_payload


def test_payment_log_redaction_under_load(caplog):
    with caplog.at_level(logging.INFO):
        for index in range(1000):
            payload = {
                "PhoneNumber": "+254712630003",
                "CheckoutRequestID": f"ws_CO_LOG_PRESSURE_{index}",
                "MerchantRequestID": f"merchant-log-pressure-{index}",
                "MpesaReceiptNumber": f"QLOGPRESSURE{index:04d}",
                "access_token": f"token-log-pressure-{index}",
            }
            logging.getLogger("checkout-log-pressure").info("payload=%s", redact_checkout_payload(payload))

    assert "+254712630003" not in caplog.text
    assert "ws_CO_LOG_PRESSURE_999" not in caplog.text
    assert "merchant-log-pressure-999" not in caplog.text
    assert "QLOGPRESSURE0999" not in caplog.text
    assert "token-log-pressure-999" not in caplog.text
