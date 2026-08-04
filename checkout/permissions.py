from urllib.parse import urlparse

from django.conf import settings

from billing.permissions import IsSafaricomIP
from checkout.webhook_auth import HasMpesaWebhookSharedSecret


class IsSafaricomCheckoutIP(IsSafaricomIP):
    """
    Preserve strict production Daraja IP allowlisting.

    Sandbox-only exception: Safaricom sandbox callbacks can be verified through
    ephemeral HTTPS tunnels. The exception is allowed only when:
    - DARAJA_ENV=sandbox
    - DARAJA_SANDBOX_ALLOW_TUNNEL_CALLBACKS is explicitly true (or DEBUG)
    - callback URL host is an approved tunnel domain and matches request Host
    """

    def _is_sandbox_tunnel_callback(self, request):
        if getattr(settings, "DARAJA_ENV", "") != "sandbox":
            return False
        allow_tunnel = getattr(settings, "DARAJA_SANDBOX_ALLOW_TUNNEL_CALLBACKS", False) or getattr(
            settings, "DEBUG", False
        )
        if not allow_tunnel:
            return False

        callback_url = getattr(settings, "DARAJA_CALLBACK_URL", "")
        parsed_callback = urlparse(callback_url)
        callback_host = (parsed_callback.hostname or "").lower()
        if parsed_callback.scheme != "https" or not callback_host:
            return False

        allowed_domains = getattr(settings, "DARAJA_SANDBOX_CALLBACK_TUNNEL_DOMAINS", [])
        if not any(callback_host == domain or callback_host.endswith(f".{domain}") for domain in allowed_domains):
            return False

        request_host = request.get_host().split(":")[0].lower()
        if request_host != callback_host:
            return False

        forwarded_proto = request.META.get("HTTP_X_FORWARDED_PROTO", "")
        return request.is_secure() or forwarded_proto == "https"

    def has_permission(self, request, view):
        if self._is_sandbox_tunnel_callback(request):
            return True
        return super().has_permission(request, view)


class IsAuthorizedMpesaWebhook(IsSafaricomCheckoutIP):
    """IP/tunnel allowlist AND shared-secret gate (when required or configured)."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return HasMpesaWebhookSharedSecret().has_permission(request, view)
