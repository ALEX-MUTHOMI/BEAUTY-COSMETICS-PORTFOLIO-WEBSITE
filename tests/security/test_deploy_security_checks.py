"""Deploy-check proofs: weak secrets and live webhook secret fail closed."""

import pytest
from django.core.checks import run_checks
from django.test import override_settings


@pytest.mark.django_db
@override_settings(
    DEBUG=False,
    SECRET_KEY="django-insecure-ci-placeholder-key-32-chars",
    PII_HASH_PEPPER="local-test-pii-hash-pepper-change-me",
    PII_ENCRYPTION_KEY="local-test-pii-encryption-key-change-me",
    TURNSTILE_SECRET_KEY="1x0000000000000000000000000000000AA",
    PAYMENT_PROVIDER_MODE="fake",
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
    DEBUG=False,
    SECRET_KEY="production-grade-secret-key-with-enough-entropy-xyz",
    PII_HASH_PEPPER="production-grade-pii-hash-pepper-value",
    PII_ENCRYPTION_KEY="production-grade-pii-encryption-key",
    TURNSTILE_SECRET_KEY="live-turnstile-secret-not-the-test-one",
    PAYMENT_PROVIDER_MODE="daraja_live",
    MPESA_WEBHOOK_SHARED_SECRET="",
)
def test_deploy_checks_require_webhook_secret_in_live_mode():
    errors = {
        e.id for e in run_checks(tags=["security"], include_deployment_checks=True) if e.id.startswith("aesthetic_os.")
    }
    assert "aesthetic_os.E004" in errors


@pytest.mark.django_db
@override_settings(
    DEBUG=False,
    SECRET_KEY="production-grade-secret-key-with-enough-entropy-xyz",
    PII_HASH_PEPPER="production-grade-pii-hash-pepper-value",
    PII_ENCRYPTION_KEY="production-grade-pii-encryption-key",
    TURNSTILE_SECRET_KEY="live-turnstile-secret-not-the-test-one",
    PAYMENT_PROVIDER_MODE="daraja_live",
    MPESA_WEBHOOK_SHARED_SECRET="super-secret-webhook-token-32chars!!",
)
def test_deploy_checks_pass_with_strong_live_config():
    errors = [
        e for e in run_checks(tags=["security"], include_deployment_checks=True) if e.id.startswith("aesthetic_os.")
    ]
    assert errors == []
