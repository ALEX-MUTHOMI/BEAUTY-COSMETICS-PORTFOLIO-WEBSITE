from checkout.redaction import (
    hash_sensitive_value,
    redact_checkout_payload,
    redact_phone,
)


def test_checkout_redaction_masks_payment_identifiers(settings):
    settings.SECRET_KEY = "checkout-redaction-secret"  # nosec
    payload = {
        "PhoneNumber": "+254712200006",
        "MpesaReceiptNumber": "QCHECKOUTRAW",
        "CheckoutRequestID": "ws_CO_CHECKOUT_RAW",
        "MerchantRequestID": "merchant-raw",
    }

    redacted = redact_checkout_payload(payload)

    assert "+254712200006" not in str(redacted)
    assert "QCHECKOUTRAW" not in str(redacted)
    assert "ws_CO_CHECKOUT_RAW" not in str(redacted)
    assert "merchant-raw" not in str(redacted)
    assert redact_phone("+254712200006") == "+2547***006"
    assert hash_sensitive_value("ws_CO_CHECKOUT_RAW") != "ws_CO_CHECKOUT_RAW"
