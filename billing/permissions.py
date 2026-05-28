import ipaddress

from django.conf import settings
from rest_framework.permissions import BasePermission


class IsSafaricomIP(BasePermission):
    """
    Restricts Daraja callbacks to configured Safaricom CIDRs.
    X-Forwarded-For is trusted only when REMOTE_ADDR is a configured trusted proxy.
    """

    message = "Daraja callback source IP is not allowed."

    def _client_ip(self, request):
        remote_addr = request.META.get("REMOTE_ADDR", "")
        trusted_proxies = [
            ipaddress.ip_network(cidr.strip()) for cidr in getattr(settings, "TRUSTED_PROXY_CIDRS", []) if cidr.strip()
        ]

        try:
            remote_ip = ipaddress.ip_address(remote_addr)
        except ValueError:
            return remote_addr

        if any(remote_ip in proxy for proxy in trusted_proxies):
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            first_hop = forwarded_for.split(",")[0].strip()
            if first_hop:
                return first_hop
        return remote_addr

    def has_permission(self, request, view):
        try:
            client_ip = ipaddress.ip_address(self._client_ip(request))
        except ValueError:
            return False

        allowed_networks = [
            ipaddress.ip_network(cidr.strip()) for cidr in settings.SAFARICOM_ALLOWED_CIDRS if cidr.strip()
        ]
        return any(client_ip in network for network in allowed_networks)
