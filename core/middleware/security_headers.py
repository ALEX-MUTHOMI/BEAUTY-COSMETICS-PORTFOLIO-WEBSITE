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
    def _corp_policy(path: str) -> str:
        # Nuxt (:3000) credentialed fetches to Django (:8000) are cross-origin.
        # CORP same-origin blocks those reads even when CORS allows the SPA.
        # Keep same-origin for non-API surfaces; allow cross-origin only for /api/.
        if path.startswith("/api/"):
            return "cross-origin"
        return "same-origin"

    @staticmethod
    def _apply_security_headers(request: HttpRequest, response: HttpResponse) -> None:
        path = request.path_info or request.path
        csp = ADMIN_CONTENT_SECURITY_POLICY if path.startswith("/admin/") else CONTENT_SECURITY_POLICY
        response.headers.setdefault("Content-Security-Policy", csp)
        response.headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        response.headers.setdefault("Cross-Origin-Resource-Policy", SecurityHeadersMiddleware._corp_policy(path))
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "same-origin")

    @staticmethod
    def _should_disable_cache(request: HttpRequest, response: HttpResponse) -> bool:
        path = request.path_info or request.path
        return response.status_code >= 400 or any(path.startswith(prefix) for prefix in NO_STORE_PREFIXES)

    @staticmethod
    def _apply_no_store(response: HttpResponse) -> None:
        existing_cache_control = response.headers.get("Cache-Control", "")
        if "no-store" not in existing_cache_control.lower():
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
