"""Staff-aware CSRF failure handling — audit login_failed without passwords."""

from django.conf import settings
from django.views.csrf import csrf_failure as django_csrf_failure

from bookings.models import StaffSecurityAudit
from bookings.services.staff_auth import (
    LOGIN_FAILURE_REASON_CSRF,
    LOGIN_FAILURE_REASON_SESSION,
    LOGIN_FAILURE_REASON_TRANSPORT,
    audit_staff_event,
)

_STAFF_LOGIN_PREFIXES = (
    "/api/staff/auth/login",
    "/api/staff/auth/login/",
)


def _classify_staff_login_csrf_reason(request, reason=""):
    """Map detectable CSRF/session/transport classes for staff login audits."""
    secure_cookies = bool(getattr(settings, "SESSION_COOKIE_SECURE", False)) or bool(
        getattr(settings, "CSRF_COOKIE_SECURE", False)
    )
    if secure_cookies and not request.is_secure():
        return LOGIN_FAILURE_REASON_TRANSPORT

    reason_text = str(reason or "").lower()
    if "csrf cookie not set" in reason_text or "session" in reason_text:
        return LOGIN_FAILURE_REASON_SESSION
    return LOGIN_FAILURE_REASON_CSRF


def staff_aware_csrf_failure(request, reason=""):
    """
    CSRF_FAILURE_VIEW: audit staff login CSRF/session/transport failures, then
    return Django's generic CSRF response (never passwords or raw tokens).
    """
    path = getattr(request, "path", "") or ""
    if path.rstrip("/") == "/api/staff/auth/login" or path in _STAFF_LOGIN_PREFIXES:
        failure_reason = _classify_staff_login_csrf_reason(request, reason)
        audit_staff_event(
            StaffSecurityAudit.EventType.LOGIN_FAILURE,
            request=request,
            metadata={
                "reason": failure_reason,
                "channel": "password",
                "login_failed": True,
            },
        )
    return django_csrf_failure(request, reason=reason)
