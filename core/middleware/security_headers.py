from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'"
)
ADMIN_CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'"
)
PERMISSIONS_POLICY = (
    "accelerometer=(), autoplay=(), camera=(), clipboard-read=(), "
    "clipboard-write=(), geolocation=(), gyroscope=(), magnetometer=(), "
    "microphone=(), payment=(), usb=(), browsing-topics=()"
)

NO_STORE_PREFIXES = (
    "/health/",
    "/api/health-check/",
    "/api/csrf/",
    "/api/schema/",
    "/api/auth/",
    "/api/billing/",
    "/api/bookings/",
    "/api/checkout/",
    "/api/customers/",
    "/api/legal/",
    "/api/staff/",
)


class SecurityHeadersMiddleware:
    """Apply consistent browser security and no-store policy to API responses."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        self._apply_security_headers(request, response)
        if self._should_disable_cache(request, response):
            self._apply_no_store(response)
        return response

    @staticmethod
    def _apply_security_headers(request: HttpRequest, response: HttpResponse) -> None:
        csp = ADMIN_CONTENT_SECURITY_POLICY if request.path_info.startswith("/admin/") else CONTENT_SECURITY_POLICY
        response.headers.setdefault("Content-Security-Policy", csp)
        response.headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "same-origin")

    @staticmethod
    def _should_disable_cache(request: HttpRequest, response: HttpResponse) -> bool:
        path = request.path_info or request.path
        return response.status_code >= 400 or any(path.startswith(prefix) for prefix in NO_STORE_PREFIXES)

    @staticmethod
    def _apply_no_store(response: HttpResponse) -> None:
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
