"""Fail-closed public booking until an operator explicitly opens it for go-live."""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

# Money-path and slot booking only. Catalog, privacy rights, booking status,
# M-Pesa webhooks, staff, and health stay reachable.
BLOCKED_PREFIXES = (
    "/api/bookings/calendar/",
    "/api/bookings/availability/",
    "/api/bookings/holds/",
    "/api/bookings/checkout/",
    "/api/checkout/sessions/",
)

CLOSED_BODY = {
    "detail": "Public booking is closed pending launch.",
    "code": "public_booking_closed",
}


class PublicBookingGateMiddleware:
    """Return HTTP 503 for public booking APIs when PUBLIC_BOOKING_ENABLED is off."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if getattr(settings, "PUBLIC_BOOKING_ENABLED", False):
            return self.get_response(request)
        path = request.path_info or request.path
        if any(path.startswith(prefix) for prefix in BLOCKED_PREFIXES):
            response = JsonResponse(CLOSED_BODY, status=503)
            response["Retry-After"] = "3600"
            response["Cache-Control"] = "no-store"
            return response
        return self.get_response(request)
