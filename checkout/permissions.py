from urllib.parse import urlparse

from django.conf import settings

from billing.permissions import IsSafaricomIP


class IsSafaricomCheckoutIP(IsSafaricomIP):
    """
    Preserve strict production Daraja IP allowlisting.

    Sandbox-only exception: Safaricom sandbox callbacks can be verified through
    ephemeral HTTPS tunnels. The exception is allowed only when the configured
    callback URL itself points at an approved tunnel host and the request Host
    matches that exact tunnel host.
    """

    def _is_sandbox_tunnel_callback(self, request):
        if getattr(settings, "DARAJA_ENV", "") != "sandbox":
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
