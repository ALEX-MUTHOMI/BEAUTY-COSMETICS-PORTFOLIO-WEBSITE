"""Deploy-time security checks (fail closed for real-money / non-DEBUG)."""

from __future__ import annotations

from django.conf import settings
from django.core.checks import Error, Tags, register

_WEAK_SECRET_MARKERS = (
    "django-insecure-",
    "phase1-phase2-",
    "ci-placeholder",
    "change-me",
    "local-test-",
)
_TURNSTILE_TEST_SECRET = "1x0000000000000000000000000000000AA"


@register(Tags.security, deploy=True)
def check_production_secrets(app_configs, **kwargs):
    """Reject known-weak secrets when running check --deploy."""
    errors = []
    if getattr(settings, "DEBUG", True):
        return errors

    secret = str(getattr(settings, "SECRET_KEY", "") or "")
    if not secret or any(marker in secret for marker in _WEAK_SECRET_MARKERS):
        errors.append(
            Error(
                "SECRET_KEY is missing or uses a known-weak/default value.",
                hint="Inject a high-entropy SECRET_KEY before production cutover.",
                id="aesthetic_os.E001",
            )
        )

    for name in ("PII_HASH_PEPPER", "PII_ENCRYPTION_KEY"):
        value = str(getattr(settings, name, "") or "")
        if len(value) < 24 or any(marker in value for marker in _WEAK_SECRET_MARKERS):
            errors.append(
                Error(
                    f"{name} is missing, too short, or uses a known-weak default.",
                    hint=f"Set a dedicated {name} (≥24 chars) for booking PII protection.",
                    id="aesthetic_os.E002",
                )
            )

    turnstile = str(getattr(settings, "TURNSTILE_SECRET_KEY", "") or "")
    if turnstile == _TURNSTILE_TEST_SECRET:
        errors.append(
            Error(
                "TURNSTILE_SECRET_KEY is still Cloudflare's public test placeholder.",
                hint="Configure a live Turnstile secret before production.",
                id="aesthetic_os.E003",
            )
        )
    return errors


@register(Tags.security, deploy=True)
def check_mpesa_webhook_shared_secret(app_configs, **kwargs):
    """Live/real money modes must have an edge webhook shared secret at boot."""
    from checkout.webhook_auth import webhook_shared_secret_required

    if not webhook_shared_secret_required():
        return []
    secret = str(getattr(settings, "MPESA_WEBHOOK_SHARED_SECRET", "") or "").strip()
    if secret:
        return []
    return [
        Error(
            "MPESA_WEBHOOK_SHARED_SECRET is required for live/real Daraja payment mode.",
            hint="Set MPESA_WEBHOOK_SHARED_SECRET (and prefer REQUIRE=true) before enabling real money.",
            id="aesthetic_os.E004",
        )
    ]
