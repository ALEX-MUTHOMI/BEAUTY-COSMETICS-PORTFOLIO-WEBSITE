import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from bookings.models import StaffSecurityAudit
from bookings.services.staff_auth import (
    GENERIC_REAUTH_REQUIRED,
    GENERIC_SESSION_EXPIRED,
    audit_staff_event,
    enforce_staff_session,
    has_recent_staff_auth,
)
from bookings.services.staff_portal import (
    StaffBookingNotFound,
    StaffPortalValidationError,
    get_booking_detail,
    get_daily_schedule,
    get_payment_summary,
    get_weekly_overview,
    reveal_contact,
)
from core.abuse import record_abuse_signal
from core.throttling import route_throttle, staff_or_ip_identity


def _json(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _request_payload(request):
    content_type = str(request.META.get("CONTENT_TYPE", "") or "")
    if "application/json" in content_type:
        try:
            payload = json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}
    return request.POST


def _forbidden():
    return _json({"detail": "Staff portal is unavailable."}, status=403)


def _session_expired():
    return _json({"detail": GENERIC_SESSION_EXPIRED}, status=403)


def _recent_reauth_required():
    return _json({"detail": GENERIC_REAUTH_REQUIRED}, status=403)


def _has_staff_permission(user, codename):
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_staff", False):
        return False
    return bool(getattr(user, "is_superuser", False) or user.has_perm(f"bookings.{codename}"))


def _require_staff_permission(request, codename):
    if not getattr(request.user, "is_authenticated", False) or not getattr(request.user, "is_staff", False):
        return _forbidden()
    if not enforce_staff_session(request):
        return _session_expired()
    if not _has_staff_permission(request.user, codename):
        audit_staff_event(
            StaffSecurityAudit.EventType.PERMISSION_DENIED,
            staff_user=request.user,
            request=request,
            metadata={"permission": codename},
        )
        return _forbidden()
    return None


def _not_found():
    return _json({"detail": "Staff booking record is unavailable."}, status=404)


def _validation_error():
    return _json({"detail": "Staff booking request is invalid."}, status=400)


@require_GET
def staff_booking_schedule(request):
    denied = _require_staff_permission(request, "view_staff_portal")
    if denied:
        return denied
    try:
        payload = get_daily_schedule(
            request.GET.get("date"),
            filters={
                "status": request.GET.get("status", ""),
                "booking_type": request.GET.get("booking_type", ""),
            },
        )
    except StaffPortalValidationError:
        return _validation_error()
    return _json(payload)


@require_GET
def staff_booking_week(request):
    denied = _require_staff_permission(request, "view_staff_portal")
    if denied:
        return denied
    try:
        payload = get_weekly_overview(request.GET.get("start_date"))
    except StaffPortalValidationError:
        return _validation_error()
    return _json(payload)


@require_GET
def staff_booking_detail(request, public_booking_id):
    denied = _require_staff_permission(request, "view_staff_booking")
    if denied:
        return denied
    try:
        payload = get_booking_detail(public_booking_id)
    except StaffBookingNotFound:
        return _not_found()
    return _json(payload)


@require_GET
def staff_booking_payment(request, public_booking_id):
    denied = _require_staff_permission(request, "view_staff_payment_summary")
    if denied:
        return denied
    try:
        payload = get_payment_summary(public_booking_id)
    except StaffBookingNotFound:
        return _not_found()
    return _json(payload)


@require_POST
@route_throttle("staff_contact_reveal", key_builder=staff_or_ip_identity)
def staff_booking_contact_access(request, public_booking_id):
    denied = _require_staff_permission(request, "view_staff_contact_details")
    if denied:
        # A non-staff or under-permissioned caller probing a contact endpoint is
        # materially different from a normal staff workflow. The score is
        # route-scoped and still returns the same generic 403 for this request.
        record_abuse_signal(
            request,
            scope="staff_contact_reveal",
            event_type="STAFF_CONTACT_PROBING",
            points=4,
        )
        return denied
    if not has_recent_staff_auth(request):
        record_abuse_signal(
            request,
            scope="staff_contact_reveal",
            event_type="CONTACT_REAUTH_BYPASS_ATTEMPT",
            points=2,
        )
        return _recent_reauth_required()
    try:
        payload = reveal_contact(
            public_booking_id,
            staff_user=request.user,
            reason=str(_request_payload(request).get("reason", "")),
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
    except StaffBookingNotFound:
        return _not_found()
    except StaffPortalValidationError:
        return _validation_error()
    audit_staff_event(
        StaffSecurityAudit.EventType.CONTACT_REVEAL,
        staff_user=request.user,
        request=request,
        metadata={"booking_reference": public_booking_id},
    )
    return _json(payload)
