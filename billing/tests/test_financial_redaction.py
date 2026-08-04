from billing.redaction import (
    hash_sensitive_value,
    redact_financial_payload,
    redact_phone,
)


def test_financial_redaction_masks_phone_receipt_and_provider_ids(settings):
    settings.SECRET_KEY = "redaction-test-secret"  # nosec
    payload = {
        "PhoneNumber": "+254712345678",
        "MpesaReceiptNumber": "QRAWRECEIPT123",
        "CheckoutRequestID": "ws_CO_RAW_CHECKOUT",
        "nested": {"MerchantRequestID": "raw-merchant-id"},
    }

    redacted = redact_financial_payload(payload)

    assert "+254712345678" not in str(redacted)
    assert "QRAWRECEIPT123" not in str(redacted)
    assert "ws_CO_RAW_CHECKOUT" not in str(redacted)
    assert "raw-merchant-id" not in str(redacted)
    assert redact_phone("+254712345678") == "+2547***678"
    assert hash_sensitive_value("QRAWRECEIPT123") != "QRAWRECEIPT123"
