import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from bookings.services.availability import AvailabilityService
from bookings.services.booking_calendar import BookingCalendarService
from bookings.services.catalog import list_public_full_packages, list_public_services
from bookings.services.catalog_resolve import resolve_catalog_selection
from bookings.services.checkout_contract import BookingCheckoutContractService
from bookings.services.guest_stk import initiate_guest_booking_stk
from bookings.services.handoff_resolve import resolve_booking_handoff
from bookings.services.hold_bot_guard import require_hold_turnstile_if_abused
from bookings.services.holds import BookingHoldService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT
from core.middleware.correlation_id import get_correlation_id
from core.throttling import route_throttle
from users.services import get_redis_client

GENERIC_AVAILABILITY_ERROR = "Availability unavailable."
GENERIC_CALENDAR_ERROR = "Calendar unavailable."
GENERIC_RESOLVE_ERROR = "Selection unavailable."
GENERIC_HOLD_ERROR = "Booking request could not be accepted."
GENERIC_CHECKOUT_ERROR = "Checkout request could not be accepted."
GENERIC_STK_ERROR = "Payment could not be started."
FORBIDDEN_CLIENT_FIELDS = {
    "amount",
    "base_price",
    "currency",
    "duration",
    "duration_minutes",
    "price",
    "total_amount",
}


def _json(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _get_redis_client_safe():
    # Hold creation must never fail because the circuit-breaker signal is
    # unavailable; BookingHoldService/_safe_counter already treat a missing
    # or misbehaving client as a no-op / fail-safe LOCKDOWN read.
    try:
        return get_redis_client()
    except Exception:
        return None


def _request_context(request, payload=None):
    payload = payload or {}
    return {
        "request_id": get_correlation_id(),
        "ip": request.META.get("REMOTE_ADDR", ""),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "policy_acceptance": payload.get("policy_acceptance"),
        "redis_client": _get_redis_client_safe(),
    }


def _parse_starts_at(value):
    try:
        parsed = datetime.fromisoformat(str(value or ""))
    except ValueError as exc:
        raise ValidationError(GENERIC_HOLD_ERROR) from exc
    if parsed.tzinfo is None:
        raise ValidationError(GENERIC_HOLD_ERROR)
    return parsed


def _client_price_tampering_present(payload):
    return bool(FORBIDDEN_CLIENT_FIELDS.intersection(payload.keys()))


def _safe_hold_payload(hold):
    return {
        "booking_public_id": hold["booking_public_id"],
        "status": hold["status"],
        "hold_expires_at": hold["hold_expires_at"],
        "starts_at": hold["starts_at"],
        "ends_at": hold["ends_at"],
        "selection": hold.get("selection") or {},
        "next_action": hold["next_action"],
        "hold_ttl_minutes": hold["hold_ttl_minutes"],
    }


@require_GET
def catalog_services(_request):
    return _json({"services": list_public_services()})


@require_GET
def catalog_packages(_request):
    return _json({"packages": list_public_full_packages()})


@require_GET
@route_throttle("catalog_resolve")
def catalog_resolve(request):
    try:
        selection = resolve_catalog_selection(
            selection_type=request.GET.get("selection_type"),
            slug=request.GET.get("slug"),
        )
    except ValidationError:
        return _json({"detail": GENERIC_RESOLVE_ERROR}, status=400)
    except Exception:
        return _json({"detail": GENERIC_RESOLVE_ERROR}, status=400)
    return _json({"selection": selection.to_api_payload()})


@require_GET
@route_throttle("catalog_resolve")
def catalog_resolve_handoff(request):
    try:
        selection = resolve_booking_handoff(
            handoff_type=request.GET.get("type"),
            plan_slug=request.GET.get("plan"),
            category_slug=request.GET.get("category"),
            treatment_slug=request.GET.get("treatment"),
        )
    except ValidationError:
        return _json({"detail": GENERIC_RESOLVE_ERROR}, status=400)
    except Exception:
        return _json({"detail": GENERIC_RESOLVE_ERROR}, status=400)
    return _json({"selection": selection.to_api_payload()})


@require_GET
@route_throttle("booking_calendar")
def booking_calendar(request):
    selection_type = str(request.GET.get("selection_type") or "normal")
    try:
        calendar = BookingCalendarService.build_calendar(
            selection_type=selection_type,
            service_public_id=request.GET.get("service_public_id"),
            full_package_public_id=request.GET.get("full_package_public_id"),
            start_date=request.GET.get("start_date"),
            end_date=request.GET.get("end_date"),
            resource_id=request.GET.get("resource_public_id") or None,
            request_context=_request_context(request),
        )
    except ValidationError:
        return _json({"detail": GENERIC_CALENDAR_ERROR}, status=400)
    except Exception:
        return _json({"detail": GENERIC_CALENDAR_ERROR}, status=400)
    return _json({"calendar": calendar})


@require_GET
@route_throttle("availability")
def booking_availability(request):
    selection_type = str(request.GET.get("selection_type") or "normal")
    try:
        if selection_type == "full_package":
            result = AvailabilityService.get_full_package_available_slots(
                request.GET.get("full_package_public_id"),
                request.GET.get("start_date"),
                request.GET.get("end_date"),
                resource_id=request.GET.get("resource_public_id") or None,
            )
        elif selection_type == "bundle":
            service_ids = [value for value in str(request.GET.get("service_public_ids") or "").split(",") if value]
            result = AvailabilityService.get_bundle_available_slots(
                service_ids,
                request.GET.get("start_date"),
                request.GET.get("end_date"),
                resource_id=request.GET.get("resource_public_id") or None,
            )
        else:
            result = AvailabilityService.get_available_slots(
                request.GET.get("service_public_id"),
                request.GET.get("start_date"),
                request.GET.get("end_date"),
                resource_id=request.GET.get("resource_public_id") or None,
            )
    except ValidationError:
        return _json({"detail": GENERIC_AVAILABILITY_ERROR}, status=400)
    return _json({"availability": result})


@require_POST
@route_throttle("booking_hold")
def booking_hold_create(request):
    payload = _body(request)
    if _client_price_tampering_present(payload):
        return _json({"detail": GENERIC_HOLD_ERROR}, status=400)
    try:
        redis_client = _get_redis_client_safe()
        require_hold_turnstile_if_abused(
            request=request,
            payload=payload,
            redis_client=redis_client,
        )
        starts_at = _parse_starts_at(payload.get("starts_at"))
        customer = payload.get("customer") or {}
        selection_type = str(payload.get("selection_type") or "normal")
        request_context = _request_context(request, payload)
        request_context["redis_client"] = redis_client
        if selection_type == "full_package":
            hold = BookingHoldService.create_full_package_hold(
                full_package_public_id=payload.get("full_package_public_id"),
                resource_public_id=payload.get("resource_public_id") or None,
                starts_at=starts_at,
                customer_payload=customer,
                idempotency_key=payload.get("idempotency_key"),
                request_context=request_context,
                client_package_items=payload.get("package_items"),
            )
        elif selection_type == "bundle":
            hold = BookingHoldService.create_bundle_hold(
                service_public_ids=payload.get("service_public_ids") or [],
                resource_public_id=payload.get("resource_public_id") or None,
                starts_at=starts_at,
                customer_payload=customer,
                idempotency_key=payload.get("idempotency_key"),
                request_context=request_context,
            )
        else:
            hold = BookingHoldService.create_hold(
                service_public_id=payload.get("service_public_id"),
                resource_public_id=payload.get("resource_public_id") or None,
                starts_at=starts_at,
                customer_payload=customer,
                idempotency_key=payload.get("idempotency_key"),
                request_context=request_context,
            )
    except ValidationError:
        return _json({"detail": GENERIC_HOLD_ERROR}, status=400)
    return _json({"booking": _safe_hold_payload(hold)}, status=201)


@require_POST
@route_throttle("booking_checkout")
def booking_checkout_create(request):
    payload = _body(request)
    policy_acceptance = payload.get("policy_acceptance") or {
        "accepted": False,
        "checkbox_text": "",
    }
    try:
        checkout = BookingCheckoutContractService.create_checkout_for_held_booking(
            booking_public_id=payload.get("booking_public_id"),
            idempotency_key=payload.get("idempotency_key"),
            request_context={
                **_request_context(request, payload),
                "policy_acceptance": policy_acceptance,
            },
        )
    except ValidationError:
        return _json({"detail": GENERIC_CHECKOUT_ERROR}, status=400)
    return _json({"checkout": checkout}, status=201)


@require_POST
@route_throttle("booking_guest_stk")
def booking_guest_stk_create(request):
    """
    Guest STK — CSRF-protected, booking↔checkout bound, phone HMAC match.
    Does not use IsAuthenticated; knowledge of UUIDs alone is insufficient.
    """
    payload = _body(request)
    try:
        result = initiate_guest_booking_stk(
            booking_public_id=payload.get("booking_public_id"),
            checkout_public_id=payload.get("checkout_public_id"),
            phone_number=payload.get("phone_number"),
            idempotency_key=payload.get("idempotency_key"),
        )
    except ValidationError:
        return _json({"detail": GENERIC_STK_ERROR}, status=400)
    return _json({"stk": result}, status=202)


@require_GET
def booking_policy_acceptance_text(_request):
    return _json({"checkbox_text": POLICY_ACCEPTANCE_TEXT})
