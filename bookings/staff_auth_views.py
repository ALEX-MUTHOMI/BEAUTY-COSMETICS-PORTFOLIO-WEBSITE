import json
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from bookings.models import StaffSecurityAudit
from bookings.services.staff_auth import (
    GENERIC_INVALID_CREDENTIALS,
    GENERIC_RATE_LIMITED,
    GENERIC_RESET_INVALID,
    GENERIC_RESET_RESPONSE,
    GENERIC_SESSION_EXPIRED,
    StaffAuthError,
    StaffAuthRateLimited,
    assert_login_not_throttled,
    audit_staff_event,
    clear_login_failures,
    confirm_staff_password_reset,
    enforce_staff_session,
    mark_staff_recent_auth,
    mark_staff_session_authenticated,
    record_login_failure,
    request_staff_password_reset,
    staff_profile,
)
from bookings.services.staff_oauth import (
    StaffOAuthError,
    complete_staff_oauth_login,
    exchange_authorization_code,
    login_failure_redirect,
    provider_is_ready,
    resolve_provider_email,
    safe_portal_redirect,
)
from core.throttling import route_throttle, staff_or_ip_identity


def _json(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _body(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _staff_forbidden():
    return _json({"detail": "Staff portal is unavailable."}, status=403)


def _safe_next_path(next_path):
    next_path = str(next_path or "").strip()
    if (
        not next_path
        or not next_path.startswith("/")
        or next_path.startswith("//")
        or not next_path.startswith("/staff/")
        or "\r" in next_path
        or "\n" in next_path
    ):
        return "/staff/dashboard"
    return next_path


def _oauth_setting(provider, name, default=""):
    return getattr(settings, f"STAFF_{provider.upper()}_OAUTH_{name}", default)


def _staff_oauth_start(request, provider):
    if not provider_is_ready(provider):
        # Fail closed: incomplete OAuth config never starts a provider hop.
        return _json({"detail": "Not found."}, status=404)

    client_id = _oauth_setting(provider, "CLIENT_ID")
    redirect_uri = _oauth_setting(provider, "REDIRECT_URI")
    auth_url = _oauth_setting(provider, "AUTH_URL")
    scope = _oauth_setting(provider, "SCOPE", "openid email profile")
    response_mode = _oauth_setting(provider, "RESPONSE_MODE", "")

    state = secrets.token_urlsafe(32)
    request.session[f"staff_{provider}_oauth_state"] = state
    request.session[f"staff_{provider}_oauth_next"] = _safe_next_path(request.GET.get("next"))
    request.session.modified = True

    query = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state,
    }
    if response_mode:
        query["response_mode"] = response_mode

    response = HttpResponseRedirect(f"{auth_url}?{urlencode(query)}")
    response["Cache-Control"] = "no-store"
    response["Referrer-Policy"] = "no-referrer"
    return response


def _oauth_callback_params(request):
    if request.method == "POST":
        return request.POST
    return request.GET


def _staff_oauth_callback(request, provider):
    if not provider_is_ready(provider):
        return HttpResponseRedirect(login_failure_redirect())

    params = _oauth_callback_params(request)
    if params.get("error"):
        return HttpResponseRedirect(login_failure_redirect())

    state = str(params.get("state") or "")
    code = str(params.get("code") or "")
    expected = str(request.session.pop(f"staff_{provider}_oauth_state", "") or "")
    next_path = _safe_next_path(request.session.pop(f"staff_{provider}_oauth_next", "/staff/dashboard"))
    request.session.modified = True

    if not state or not expected or not secrets.compare_digest(state, expected) or not code:
        audit_staff_event(
            StaffSecurityAudit.EventType.LOGIN_FAILURE,
            request=request,
            metadata={"provider": provider, "reason": "oauth_state_or_code"},
        )
        return HttpResponseRedirect(login_failure_redirect())

    try:
        token_payload = exchange_authorization_code(provider, code)
        email = resolve_provider_email(provider, token_payload)
        complete_staff_oauth_login(request, provider=provider, email=email)
    except StaffOAuthError as exc:
        # staff_not_provisioned is already audited inside complete_staff_oauth_login.
        reason = str(exc) or "oauth_failed"
        if reason != "staff_not_provisioned":
            audit_staff_event(
                StaffSecurityAudit.EventType.LOGIN_FAILURE,
                request=request,
                metadata={"provider": provider, "reason": reason, "channel": "oauth"},
            )
        return HttpResponseRedirect(login_failure_redirect())

    response = HttpResponseRedirect(safe_portal_redirect(next_path))
    response["Cache-Control"] = "no-store"
    response["Referrer-Policy"] = "no-referrer"
    return response


@require_POST
@route_throttle("staff_login", key_builder=staff_or_ip_identity)
def staff_login(request):
    """Authenticate staff via password. Authorization (portal perms) is enforced on staff APIs."""
    payload = _body(request)
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    try:
        assert_login_not_throttled(email, request)
    except StaffAuthRateLimited:
        return _json({"detail": GENERIC_RATE_LIMITED}, status=429)

    user = authenticate(request, username=email, password=password)
    # Authn gate: active + is_staff. Unknown user / bad password / non-staff share one client message.
    if not user or not getattr(user, "is_active", False) or not getattr(user, "is_staff", False):
        reason = "not_staff" if user and not getattr(user, "is_staff", False) else "invalid_credentials"
        record_login_failure(
            email,
            request,
            staff_user=user if getattr(user, "is_staff", False) else None,
            reason=reason,
        )
        return _json({"detail": GENERIC_INVALID_CREDENTIALS}, status=400)

    login(request, user)
    mark_staff_session_authenticated(request)
    clear_login_failures(email, request)
    audit_staff_event(
        StaffSecurityAudit.EventType.LOGIN_SUCCESS,
        staff_user=user,
        request=request,
        metadata={"channel": "password"},
    )
    return _json(staff_profile(user))


@require_POST
def staff_logout(request):
    user = request.user if getattr(request.user, "is_authenticated", False) else None
    if user and getattr(user, "is_staff", False):
        audit_staff_event(StaffSecurityAudit.EventType.LOGOUT, staff_user=user, request=request)
    logout(request)
    return _json({"detail": "Signed out."})


@require_GET
def staff_me(request):
    if not enforce_staff_session(request):
        return _json({"detail": GENERIC_SESSION_EXPIRED}, status=403)
    return _json(staff_profile(request.user))


@require_POST
def staff_reauth(request):
    if not enforce_staff_session(request):
        return _staff_forbidden()
    payload = _body(request)
    password = str(payload.get("password", ""))
    user = authenticate(request, username=request.user.email, password=password)
    if not user or user.pk != request.user.pk:
        audit_staff_event(StaffSecurityAudit.EventType.REAUTH_FAILURE, staff_user=request.user, request=request)
        return _json({"detail": GENERIC_INVALID_CREDENTIALS}, status=400)
    mark_staff_recent_auth(request)
    audit_staff_event(StaffSecurityAudit.EventType.REAUTH_SUCCESS, staff_user=request.user, request=request)
    return _json({"detail": "Recent staff password confirmed."})


@require_POST
@route_throttle("staff_password_reset", key_builder=staff_or_ip_identity)
def staff_password_reset_request(request):
    payload = _body(request)
    request_staff_password_reset(str(payload.get("email", "")), request)
    return _json({"detail": GENERIC_RESET_RESPONSE})


@require_POST
@route_throttle("staff_password_reset", key_builder=staff_or_ip_identity)
def staff_password_reset_confirm(request):
    payload = _body(request)
    try:
        confirm_staff_password_reset(str(payload.get("token", "")), str(payload.get("new_password", "")), request)
    except (StaffAuthError, ValueError):
        return _json({"detail": GENERIC_RESET_INVALID}, status=400)
    logout(request)
    return _json({"detail": "Password reset complete."})


@require_GET
def staff_oauth_providers(request):
    """Public readiness probe — booleans only, never secrets."""
    return _json(
        {
            "google": provider_is_ready("google"),
            "apple": provider_is_ready("apple"),
        }
    )


@require_GET
@route_throttle("staff_oauth_start", key_builder=staff_or_ip_identity)
def staff_google_start(request):
    return _staff_oauth_start(request, "google")


@require_GET
@route_throttle("staff_oauth_start", key_builder=staff_or_ip_identity)
def staff_apple_start(request):
    return _staff_oauth_start(request, "apple")


@require_GET
@route_throttle("staff_oauth_callback", key_builder=staff_or_ip_identity)
def staff_google_callback(request):
    return _staff_oauth_callback(request, "google")


@csrf_exempt
@require_http_methods(["GET", "POST"])
@route_throttle("staff_oauth_callback", key_builder=staff_or_ip_identity)
def staff_apple_callback(request):
    return _staff_oauth_callback(request, "apple")
