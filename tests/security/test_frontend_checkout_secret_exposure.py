from pathlib import Path


def _production_frontend_sources() -> list[Path]:
    """Scan app source only — exclude unit/red-team fixtures that use fake MSISDNs."""
    frontend_root = Path(__file__).resolve().parents[2] / "frontend" / "src"
    paths: list[Path] = []
    for path in frontend_root.rglob("*.ts"):
        name = path.name.lower()
        if name.endswith(".spec.ts") or name.endswith(".test.ts") or ".redteam." in name:
            continue
        # PII scrubbers intentionally list secret marker names for redaction patterns.
        if "sentrypiiscrubber" in name.replace("_", "").replace("-", ""):
            continue
        paths.append(path)
    return paths


def test_frontend_checkout_resilience_code_does_not_embed_provider_secrets():
    text = "\n".join(path.read_text(errors="ignore") for path in _production_frontend_sources())

    # Real provider / ledger secret material only — not synthetic test phone fixtures.
    forbidden = [
        "DARAJA_CONSUMER_SECRET",
        "DARAJA_PASSKEY",
        "DARAJA_CONSUMER_KEY",
        "access_token",
        "MpesaReceiptNumber",
        "CheckoutRequestID",
        "MerchantRequestID",
        "Safaricom",
        "lipa_na_mpesa",
    ]
    for token in forbidden:
        assert token not in text, f"Forbidden provider token leaked into frontend source: {token}"
