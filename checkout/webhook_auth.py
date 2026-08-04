"""M-Pesa webhook shared-secret gate (edge control; Daraja does not sign callbacks)."""

from __future__ import annotations

import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission


def webhook_shared_secret_required() -> bool:
    """
    Fail-closed when real money or explicit require flag is on.

    Local/CI fake providers keep IP-only so existing suites stay green without
    inventing a secret. Live / daraja_live / production always require a secret.
    """
    if getattr(settings, "MPESA_WEBHOOK_REQUIRE_SHARED_SECRET", False):
        return True
    provider = getattr(
        settings,
        "PAYMENT_PROVIDER_MODE",
        getattr(settings, "CHECKOUT_MPESA_PROVIDER", "fake"),
    )
    if provider in {"real", "daraja_live"}:
        return True
    daraja_env = (getattr(settings, "DARAJA_ENV", "") or "").lower()
    if daraja_env in {"production", "live", "daraja_live"}:
        return True
    return False


def provided_webhook_secret(request) -> str:
    return (
        request.META.get("HTTP_X_AESTHETIC_OS_WEBHOOK_SECRET", "")
        or request.META.get("HTTP_X_CHECKOUT_WEBHOOK_SECRET", "")
        or ""
    )


class HasMpesaWebhookSharedSecret(BasePermission):
    message = "Webhook authentication failed."

    def has_permission(self, request, view):
        secret = getattr(settings, "MPESA_WEBHOOK_SHARED_SECRET", "") or ""
        required = webhook_shared_secret_required()
        if not required and not secret:
            return True
        if not secret:
            return False
        provided = provided_webhook_secret(request)
        if not provided:
            return False
        return hmac.compare_digest(provided.encode("utf-8"), secret.encode("utf-8"))
