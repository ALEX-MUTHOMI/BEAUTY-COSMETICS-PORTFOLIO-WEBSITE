import logging

from billing.redaction import redact_financial_payload


def test_billing_redaction_under_load_never_logs_raw_payment_identifiers(caplog):
    payloads = [
        {
            "PhoneNumber": f"+25471261{index:04d}"[-13:],
            "CheckoutRequestID": f"ws_CO_REDACTION_{index}",
            "MerchantRequestID": f"merchant-redaction-{index}",
            "MpesaReceiptNumber": f"QREDACTION{index:04d}",
            "access_token": f"token-redaction-{index}",
        }
        for index in range(1000)
    ]

    with caplog.at_level(logging.INFO):
        for payload in payloads:
            logging.getLogger("billing-redaction-pressure").info("payload=%s", redact_financial_payload(payload))

    output = caplog.text
    assert "ws_CO_REDACTION_999" not in output
    assert "merchant-redaction-999" not in output
    assert "QREDACTION0999" not in output
    assert "token-redaction-999" not in output
