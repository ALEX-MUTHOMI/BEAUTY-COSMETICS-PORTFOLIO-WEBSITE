import json
import logging
import os
import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.db import connection
from django.utils import timezone

from billing.redaction import hash_sensitive_value, redact_financial_payload
from bookings.models import StaffPasswordResetChallenge, StaffSecurityAudit
from bookings.privacy import normalize_email, redact_email
from users.services import get_redis_client

logger = logging.getLogger("bookings.staff_auth")

GENERIC_INVALID_CREDENTIALS = "Invalid credentials."
GENERIC_RATE_LIMITED = "Please try again later."
GENERIC_SESSION_EXPIRED = "Staff session expired. Please sign in again."
GENERIC_RESET_RESPONSE = "If the account exists, reset instructions have been sent."
GENERIC_RESET_INVALID = "Password reset request is invalid or expired."
GENERIC_REAUTH_REQUIRED = "Recent staff password confirmation required."

# Structured login_failed reason classes (never passwords). Used in StaffSecurityAudit metadata.
LOGIN_FAILURE_REASON_CSRF = "csrf"
LOGIN_FAILURE_REASON_SESSION = "session"
LOGIN_FAILURE_REASON_TRANSPORT = "transport"
LOGIN_FAILURE_REASON_INVALID_CREDENTIALS = "invalid_credentials"
LOGIN_FAILURE_REASON_LOCKOUT = "lockout"

STAFF_PORTAL_PERMISSION_CODES = {
    "manage_staff_booking_notes",
    "view_staff_booking",
    "view_staff_contact_details",
    "view_staff_payment_summary",
    "view_staff_portal",
    "confirm_staff_attendance",
    "assign_staff_booking",
    "download_staff_receipt",
    "view_staff_payments_desk",
}

_COMMON_PATTERNS = (
    "password",
    "password123",
    "beauty123",
    "makeup@2025",
    "businessname",
    "beauty business",
    "qwerty",
    "letmein",
)


class StaffAuthError(Exception):
    pass


class StaffAuthRateLimited(StaffAuthError):
    pass


def _now_timestamp():
    return timezone.now().timestamp()


def _normalize_for_comparison(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _safe_metadata(metadata):
    redacted = redact_financial_payload(metadata or {})
    text = json.dumps(redacted, sort_keys=True, default=str)
    return json.loads(text)


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "unknown") if request else "unknown"


def _user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "unknown") if request else "unknown"


def _hash_or_blank(value):
    return hash_sensitive_value(value) if value else ""


def _redis_namespace():
    current_test = os.environ.get("PYTEST_CURRENT_TEST")
    if current_test:
        return f"staff-auth:test:{os.getpid()}:{hash_sensitive_value(current_test.split(' ')[0])[:16]}"
    return "staff-auth:runtime"


def _redis_key(kind, value):
    db_name = connection.settings_dict.get("NAME", "default")
    return f"{_redis_namespace()}:{kind}:{hash_sensitive_value(f'{db_name}:{value}')}"


def _redis():
    return get_redis_client()


def validate_staff_password(password, *, email="", display_name="", business_name="AestheticOS"):
    password = str(password or "")
    if len(password) < 15:
        raise ValueError("Staff password must be at least 15 characters.")
    try:
        CommonPasswordValidator().validate(password)
    except ValidationError as exc:
        raise ValueError("Staff password is too common.") from exc

    lowered = password.lower()
    compact = _normalize_for_comparison(password)
    if any(pattern in lowered or _normalize_for_comparison(pattern) in compact for pattern in _COMMON_PATTERNS):
        raise ValueError("Staff password is too predictable.")

    candidates = []
    if email:
        candidates.append(str(email).split("@", 1)[0])
    candidates.extend(str(display_name or "").split())
    candidates.extend(str(business_name or "").split())
    candidates.append(business_name)
    for candidate in candidates:
        normalized = _normalize_for_comparison(candidate)
        if normalized and len(normalized) >= 4 and normalized in compact:
            raise ValueError("Staff password is derived from account details.")


def audit_staff_event(event_type, *, staff_user=None, request=None, metadata=None):
    """Persist a staff security audit row and emit a structured, secret-free log line."""
    safe_meta = _safe_metadata(metadata)
    event = StaffSecurityAudit.objects.create(
        staff_user=staff_user,
        event_type=event_type,
        ip_hash_hmac=_hash_or_blank(_client_ip(request)),
        user_agent_hash_hmac=_hash_or_blank(_user_agent(request)),
        metadata_redacted=safe_meta,
    )
    # Durable ops signal: event type + allowlisted ids only — never passwords/tokens/raw IP/meta JSON.
    staff_pk = getattr(staff_user, "pk", None)
    staff_token = staff_pk if isinstance(staff_pk, int) else 0
    if event_type == StaffSecurityAudit.EventType.LOGIN_FAILURE:
        logger.info("login_failed audit_id=%s staff_user_id=%s", event.public_id, staff_token)
    else:
        logger.info("staff_security_audit audit_id=%s staff_user_id=%s", event.public_id, staff_token)
    return event


def _risk_values(email, request):
    normalized = ""
    try:
        normalized = normalize_email(email)
    except ValidationError:
        normalized = str(email or "").strip().lower()
    return normalized, _client_ip(request), f"{normalized}:{_client_ip(request)}"


def _cooldown_keys(email, request):
    return [
        _redis_key(kind, value)
        for kind, value in zip(("email", "ip", "combo"), _risk_values(email, request), strict=True)
    ]


def assert_login_not_throttled(email, request):
    try:
        client = _redis()
        if any(client.exists(f"{key}:cooldown") for key in _cooldown_keys(email, request)):
            audit_staff_event(
                StaffSecurityAudit.EventType.LOGIN_RATE_LIMITED,
                request=request,
                metadata={
                    "email_redacted": _redact_email_safe(email),
                    "reason": LOGIN_FAILURE_REASON_LOCKOUT,
                    "login_failed": True,
                },
            )
            raise StaffAuthRateLimited
    except StaffAuthRateLimited:
        raise
    except Exception:
        audit_staff_event(
            StaffSecurityAudit.EventType.LOGIN_RATE_LIMITED,
            request=request,
            metadata={
                "email_redacted": _redact_email_safe(email),
                "reason": LOGIN_FAILURE_REASON_LOCKOUT,
                "detail": "rate_limit_unavailable",
                "login_failed": True,
            },
        )
        raise StaffAuthRateLimited from None


def record_login_failure(email, request, *, staff_user=None, reason=LOGIN_FAILURE_REASON_INVALID_CREDENTIALS):
    # Normalize client-indistinguishable staff-gate failures under invalid_credentials.
    audit_reason = (
        LOGIN_FAILURE_REASON_INVALID_CREDENTIALS
        if reason in {LOGIN_FAILURE_REASON_INVALID_CREDENTIALS, "not_staff"}
        else reason
    )
    metadata = {
        "email_redacted": _redact_email_safe(email),
        "reason": audit_reason,
        "channel": "password",
        "login_failed": True,
    }
    if reason == "not_staff":
        metadata["detail"] = "not_staff"
    audit_staff_event(
        StaffSecurityAudit.EventType.LOGIN_FAILURE,
        staff_user=staff_user,
        request=request,
        metadata=metadata,
    )
    try:
        client = _redis()
        limit = int(getattr(settings, "STAFF_LOGIN_FAILURE_LIMIT", 5))
        window = int(getattr(settings, "STAFF_LOGIN_FAILURE_WINDOW_SECONDS", 600))
        cooldown = int(getattr(settings, "STAFF_LOGIN_COOLDOWN_SECONDS", 600))
        for key in _cooldown_keys(email, request):
            value = client.incr(key)
            client.expire(key, window)
            if value >= limit:
                client.set(f"{key}:cooldown", "1", ex=cooldown)
    except Exception:
        return


def clear_login_failures(email, request):
    try:
        client = _redis()
        for key in _cooldown_keys(email, request):
            client.delete(key, f"{key}:cooldown")
    except Exception:
        return


def _redact_email_safe(email):
    try:
        return redact_email(email)
    except ValidationError:
        return "invalid-email"


def mark_staff_session_authenticated(request):
    now = _now_timestamp()
    request.session["staff_auth_at"] = now
    request.session["staff_last_activity_at"] = now
    request.session.pop("staff_recent_auth_at", None)
    request.session.modified = True


def mark_staff_recent_auth(request):
    request.session["staff_recent_auth_at"] = _now_timestamp()
    request.session.modified = True


def has_recent_staff_auth(request):
    value = request.session.get("staff_recent_auth_at")
    if not value:
        return False
    max_age = int(getattr(settings, "STAFF_RECENT_AUTH_TIMEOUT_SECONDS", 900))
    return _now_timestamp() - float(value) <= max_age


def enforce_staff_session(request):
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_staff", False):
        return False
    auth_at = request.session.get("staff_auth_at")
    last_activity_at = request.session.get("staff_last_activity_at")
    if not auth_at or not last_activity_at:
        audit_staff_event(StaffSecurityAudit.EventType.SESSION_EXPIRED, staff_user=user, request=request)
        logout(request)
        return False
    now = _now_timestamp()
    idle_timeout = int(getattr(settings, "STAFF_SESSION_IDLE_TIMEOUT_SECONDS", 1800))
    absolute_timeout = int(getattr(settings, "STAFF_SESSION_ABSOLUTE_TIMEOUT_SECONDS", 28800))
    if now - float(last_activity_at) > idle_timeout or now - float(auth_at) > absolute_timeout:
        audit_staff_event(StaffSecurityAudit.EventType.SESSION_EXPIRED, staff_user=user, request=request)
        logout(request)
        return False
    request.session["staff_last_activity_at"] = now
    request.session.modified = True
    return True


def staff_profile(user):
    from bookings.services.staff_roles import get_staff_role

    return {
        "display_name": _display_name(user),
        "role": get_staff_role(user),
        "permissions": sorted(
            code
            for permission in user.get_all_permissions()
            for code in [permission.split(".", 1)[1]]
            if permission.startswith("bookings.") and code in STAFF_PORTAL_PERMISSION_CODES
        ),
        "next": "/staff/dashboard",
    }


def _display_name(user):
    local = str(getattr(user, "email", "staff")).split("@", 1)[0]
    local = re.sub(r"[^a-zA-Z0-9 ._-]+", " ", local).strip()
    return local[:48] or "Staff"


def _enqueue_staff_password_reset_email(*, to_address, token, challenge_public_id, email_redacted):
    """Deliver reset token via email provider. DB stores hash only; never keep raw token in memory."""
    from bookings.infrastructure.email_provider import get_email_provider

    site = str(getattr(settings, "PUBLIC_SITE_URL", "") or getattr(settings, "FRONTEND_ORIGIN", "") or "").rstrip("/")
    reset_path = f"/staff/reset-password?token={token}"
    reset_url = f"{site}{reset_path}" if site else reset_path
    text = (
        "Staff password reset for AestheticOS.\n\n"
        f"Use this one-time link within the expiry window:\n{reset_url}\n\n"
        "If you did not request this, ignore this message."
    )
    html = f'<p>Staff password reset for AestheticOS.</p><p><a href="{reset_url}">Reset password</a></p>'
    provider = get_email_provider()
    metadata = {
        "notification_type": "staff_password_reset",
        "challenge": str(challenge_public_id),
    }
    if getattr(provider, "provider", "") in {"fake", "console"}:
        # Harvestable only from FakeEmailProvider outbox in tests — not logged.
        metadata["test_reset_token"] = token
    provider.send_email(
        to_hash=hash_sensitive_value(to_address),
        to_redacted=email_redacted,
        subject="Staff password reset",
        html=html,
        text=text,
        metadata=metadata,
        to_address=to_address,
    )


def harvest_staff_password_reset_token_for_tests():
    """Test helper: read last fake outbox reset token. Returns None outside fake provider."""
    from bookings.infrastructure.email_provider import FAKE_EMAIL_OUTBOX

    for entry in reversed(FAKE_EMAIL_OUTBOX):
        meta = entry.get("metadata") or {}
        if meta.get("notification_type") == "staff_password_reset" and meta.get("test_reset_token"):
            return meta["test_reset_token"]
    return None


def request_staff_password_reset(email, request):
    from django.contrib.auth import get_user_model

    normalized = ""
    try:
        normalized = normalize_email(email)
    except ValidationError:
        normalized = str(email or "").strip().lower()
    token = secrets.token_urlsafe(32)
    token_hash = hash_sensitive_value(token)
    staff = get_user_model().objects.filter(email__iexact=normalized, is_staff=True, is_active=True).first()
    challenge = StaffPasswordResetChallenge.objects.create(
        staff_user=staff,
        email_hash_hmac=hash_sensitive_value(normalized),
        token_hash_hmac=token_hash,
        expires_at=timezone.now()
        + timedelta(seconds=int(getattr(settings, "STAFF_PASSWORD_RESET_TOKEN_SECONDS", 1800))),
        ip_hash_hmac=_hash_or_blank(_client_ip(request)),
        user_agent_hash_hmac=_hash_or_blank(_user_agent(request)),
    )
    audit_staff_event(
        StaffSecurityAudit.EventType.PASSWORD_RESET_REQUESTED,
        staff_user=staff,
        request=request,
        metadata={"email_redacted": _redact_email_safe(normalized), "challenge": str(challenge.public_id)},
    )
    if staff:
        try:
            _enqueue_staff_password_reset_email(
                to_address=normalized,
                token=token,
                challenge_public_id=challenge.public_id,
                email_redacted=_redact_email_safe(normalized),
            )
        except Exception:
            logger.exception(
                "staff.password_reset.email_failed",
                extra={"challenge": str(challenge.public_id)},
            )
    return GENERIC_RESET_RESPONSE


def confirm_staff_password_reset(token, new_password, request):
    token_hash = hash_sensitive_value(token)
    challenge = (
        StaffPasswordResetChallenge.objects.select_related("staff_user")
        .filter(token_hash_hmac=token_hash, status=StaffPasswordResetChallenge.Status.PENDING)
        .first()
    )
    if not challenge or not challenge.staff_user or challenge.expires_at <= timezone.now():
        if challenge and challenge.status == StaffPasswordResetChallenge.Status.PENDING:
            challenge.status = StaffPasswordResetChallenge.Status.EXPIRED
            challenge.save(update_fields=["status", "updated_at"])
        raise StaffAuthError(GENERIC_RESET_INVALID)
    validate_staff_password(new_password, email=challenge.staff_user.email)
    challenge.staff_user.set_password(new_password)
    challenge.staff_user.save(update_fields=["password", "updated_at"])
    challenge.status = StaffPasswordResetChallenge.Status.USED
    challenge.used_at = timezone.now()
    challenge.save(update_fields=["status", "used_at", "updated_at"])
    audit_staff_event(
        StaffSecurityAudit.EventType.PASSWORD_RESET_COMPLETED,
        staff_user=challenge.staff_user,
        request=request,
        metadata={"challenge": str(challenge.public_id)},
    )
