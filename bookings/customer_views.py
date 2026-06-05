import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_POST

from bookings.services.remember_device import (
    cookie_name,
    create_hold_from_remembered_device,
    forget_returning_device,
    remember_confirmed_booking,
    remembered_device_summary,
    ttl_days,
)


def _json_body(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _request_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def _user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")


def _set_remember_cookie(response, token):
    max_age = ttl_days() * 24 * 60 * 60
    response.set_cookie(
        cookie_name(),
        token,
        max_age=max_age,
        httponly=True,
        secure=bool(getattr(settings, "REMEMBER_DEVICE_SECURE", not settings.DEBUG)),
        samesite=getattr(settings, "REMEMBER_DEVICE_SAMESITE", "Lax"),
        path="/",
    )


@require_POST
def remember_device(request):
    body = _json_body(request)
    try:
        token, summary = remember_confirmed_booking(
            booking_public_id=body.get("booking_public_id"),
            remember_device=body.get("remember_device") is True,
            ip=_request_ip(request),
            user_agent=_user_agent(request),
        )
    except ValidationError:
        return JsonResponse({"detail": "Remembered device is unavailable."}, status=400)
    response = JsonResponse({"remembered": True, "profile_summary": summary}, status=201)
    _set_remember_cookie(response, token)
    return response


@require_GET
def remembered_device(request):
    token = request.COOKIES.get(cookie_name(), "")
    summary = remembered_device_summary(token)
    if summary is None:
        return JsonResponse({"remembered": False})
    return JsonResponse({"remembered": True, "profile_summary": summary, "can_use_saved_details": True})


@require_POST
def use_remembered_device(request):
    body = _json_body(request)
    try:
        starts_at = parse_datetime(str(body.get("starts_at", "")))
        if starts_at is None:
            raise ValidationError("Invalid booking request.")
        result = create_hold_from_remembered_device(
            token=request.COOKIES.get(cookie_name(), ""),
            service_public_id=body.get("service_public_id"),
            resource_public_id=body.get("resource_public_id"),
            starts_at=starts_at,
            idempotency_key=body.get("idempotency_key"),
        )
    except ValidationError:
        return JsonResponse({"detail": "Remembered device is unavailable."}, status=400)
    return JsonResponse(result, status=201)


@require_POST
def forget_remembered_device(request):
    token = request.COOKIES.get(cookie_name(), "")
    forget_returning_device(token)
    response = JsonResponse({"forgotten": True})
    response.delete_cookie(cookie_name(), path="/", samesite=getattr(settings, "REMEMBER_DEVICE_SAMESITE", "Lax"))
    return response
