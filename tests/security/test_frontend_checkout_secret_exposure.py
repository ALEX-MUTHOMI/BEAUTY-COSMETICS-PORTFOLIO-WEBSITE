from pathlib import Path


def test_frontend_checkout_resilience_code_does_not_embed_provider_secrets():
    frontend_root = Path(__file__).resolve().parents[2] / "frontend" / "src"
    text = "\n".join(path.read_text(errors="ignore") for path in frontend_root.rglob("*.ts"))

    forbidden = [
        "DARAJA_CONSUMER_SECRET",
        "DARAJA_PASSKEY",
        "access_token",
        "MpesaReceiptNumber",
        "CheckoutRequestID",
        "MerchantRequestID",
        "+2547",
    ]
    for token in forbidden:
        assert token not in text
