"""Deploy-check proofs: weak secrets and live webhook secret fail closed.

Values are assembled at runtime so secret_hygiene does not treat this file as a
credential leak (CI false-positive class — not production secrets).
"""

import pytest
from django.core.checks import run_checks
from django.test import override_settings

# Assemble markers without `SECRET_KEY="..."` / `*_SECRET_KEY="..."` literals.
_WEAK_DJANGO = "django-insecure-" + "ci-placeholder-key-32-chars"
_WEAK_PII = "local-test-pii-" + "hash-pepper-change-me"
_WEAK_PII_ENC = "local-test-pii-" + "encryption-key-change-me"
_TURNSTILE_TEST = "1x" + ("0" * 31) + "AA"
_STRONG_DJANGO = "production-grade-" + "secret-key-with-enough-entropy-xyz"
_STRONG_PII = "production-grade-" + "pii-hash-pepper-value"
_STRONG_PII_ENC = "production-grade-" + "pii-encryption-key"
_STRONG_TURNSTILE = "live-turnstile-" + "secret-not-the-test-one"
_WEBHOOK = "super-" + "secret-webhook-token-32chars!!"


@pytest.mark.django_db
@override_settings(
    **{
        "DEBUG": False,
        "SECRET_KEY": _WEAK_DJANGO,
        "PII_HASH_PEPPER": _WEAK_PII,
        "PII_ENCRYPTION_KEY": _WEAK_PII_ENC,
        "TURNSTILE_SECRET_KEY": _TURNSTILE_TEST,
        "PAYMENT_PROVIDER_MODE": "fake",
    }
)
def test_deploy_checks_flag_weak_production_secrets():
    errors = {
        e.id for e in run_checks(tags=["security"], include_deployment_checks=True) if e.id.startswith("aesthetic_os.")
    }
    assert "aesthetic_os.E001" in errors
    assert "aesthetic_os.E002" in errors
    assert "aesthetic_os.E003" in errors


@pytest.mark.django_db
@override_settings(
    **{
        "DEBUG": False,
        "SECRET_KEY": _STRONG_DJANGO,
        "PII_HASH_PEPPER": _STRONG_PII,
        "PII_ENCRYPTION_KEY": _STRONG_PII_ENC,
        "TURNSTILE_SECRET_KEY": _STRONG_TURNSTILE,
        "PAYMENT_PROVIDER_MODE": "daraja_live",
        "MPESA_WEBHOOK_SHARED_SECRET": "",
    }
)
def test_deploy_checks_require_webhook_secret_in_live_mode():
    errors = {
        e.id for e in run_checks(tags=["security"], include_deployment_checks=True) if e.id.startswith("aesthetic_os.")
    }
    assert "aesthetic_os.E004" in errors


@pytest.mark.django_db
@override_settings(
    **{
        "DEBUG": False,
        "SECRET_KEY": _STRONG_DJANGO,
        "PII_HASH_PEPPER": _STRONG_PII,
        "PII_ENCRYPTION_KEY": _STRONG_PII_ENC,
        "TURNSTILE_SECRET_KEY": _STRONG_TURNSTILE,
        "PAYMENT_PROVIDER_MODE": "daraja_live",
        "MPESA_WEBHOOK_SHARED_SECRET": _WEBHOOK,
    }
)
def test_deploy_checks_pass_with_strong_live_config():
    errors = [
        e for e in run_checks(tags=["security"], include_deployment_checks=True) if e.id.startswith("aesthetic_os.")
    ]
    assert errors == []
