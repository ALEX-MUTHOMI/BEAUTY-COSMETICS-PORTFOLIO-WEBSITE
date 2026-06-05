from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from bookings.services.staff_portal import (
    StaffBookingNotFound,
    StaffPortalValidationError,
    get_booking_detail,
    get_daily_schedule,
    get_payment_summary,
    get_weekly_overview,
    reveal_contact,
)


def _json(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _forbidden():
    return _json({"detail": "Staff portal is unavailable."}, status=403)


def _has_staff_permission(user, codename):
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_staff", False):
        return False
    return bool(getattr(user, "is_superuser", False) or user.has_perm(f"bookings.{codename}"))


def _require_staff_permission(request, codename):
    if not _has_staff_permission(request.user, codename):
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
def staff_booking_contact_access(request, public_booking_id):
    denied = _require_staff_permission(request, "view_staff_contact_details")
    if denied:
        return denied
    try:
        payload = reveal_contact(
            public_booking_id,
            staff_user=request.user,
            reason=request.POST.get("reason", ""),
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
    except StaffBookingNotFound:
        return _not_found()
    except StaffPortalValidationError:
        return _validation_error()
    return _json(payload)
