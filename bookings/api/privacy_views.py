"""Public privacy subject-rights intake (ticketed, throttled, no PII echo)."""

from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from bookings.services.privacy_rights import BOOKING_PII_DATA_MAP, accept_privacy_rights_request
from core.throttling import route_throttle

GENERIC_ACCEPTED = {
    "detail": "Your privacy request was accepted and will be reviewed.",
}
GENERIC_REJECTED = {
    "detail": "Privacy request could not be accepted.",
}


@require_http_methods(["GET"])
@route_throttle("privacy_rights")
def privacy_data_map(_request):
    """Publish purpose/retention map — no customer data."""
    return JsonResponse({"data_map": BOOKING_PII_DATA_MAP, "jurisdiction": ["GDPR", "Kenya-DPA-2019"]})


@require_http_methods(["POST"])
@csrf_protect
@route_throttle("privacy_rights")
def privacy_rights_request(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse(GENERIC_REJECTED, status=400)
    if not isinstance(payload, dict):
        return JsonResponse(GENERIC_REJECTED, status=400)

    correlation_id = getattr(request, "correlation_id", "") or request.headers.get("X-Correlation-ID", "")
    ticket = accept_privacy_rights_request(
        payload,
        correlation_id=str(correlation_id),
        request_context={
            "ip": request.META.get("REMOTE_ADDR", ""),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )
    if ticket is None:
        return JsonResponse(GENERIC_REJECTED, status=400)

    body = {
        **GENERIC_ACCEPTED,
        "ticket_id": ticket.ticket_id,
        "request_type": ticket.request_type,
        "status": ticket.status,
    }
    return JsonResponse(body, status=202)
