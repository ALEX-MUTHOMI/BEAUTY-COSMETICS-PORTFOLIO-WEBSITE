"""Staff OAuth helpers — fail-closed, existing staff only (no public signup)."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import get_user_model, login

from bookings.models import StaffSecurityAudit
from bookings.services.staff_auth import (
    audit_staff_event,
    clear_login_failures,
    mark_staff_session_authenticated,
)

logger = logging.getLogger("bookings.staff_oauth")


class StaffOAuthError(Exception):
    """Generic OAuth failure — callers must not leak provider detail to clients."""


def oauth_setting(provider: str, name: str, default: str = "") -> str:
    return str(getattr(settings, f"STAFF_{provider.upper()}_OAUTH_{name}", default) or "").strip()


def provider_is_ready(provider: str) -> bool:
    return bool(
        oauth_setting(provider, "CLIENT_ID")
        and oauth_setting(provider, "CLIENT_SECRET")
        and oauth_setting(provider, "REDIRECT_URI")
        and oauth_setting(provider, "AUTH_URL")
        and oauth_setting(provider, "TOKEN_URL")
    )


def portal_public_origin() -> str:
    origin = str(getattr(settings, "STAFF_PORTAL_PUBLIC_ORIGIN", "") or "").strip().rstrip("/")
    if origin.startswith("http://") or origin.startswith("https://"):
        return origin
    return "http://localhost:3000"


def safe_portal_redirect(next_path: str) -> str:
    path = str(next_path or "").strip()
    if (
        not path
        or not path.startswith("/")
        or path.startswith("//")
        or not path.startswith("/staff/")
        or "\r" in path
        or "\n" in path
    ):
        path = "/staff/dashboard"
    return f"{portal_public_origin()}{path}"


def login_failure_redirect() -> str:
    return f"{portal_public_origin()}/staff/login?signin=unavailable"


def _http_json(
    method: str, url: str, *, data: dict[str, str] | None = None, headers: dict[str, str] | None = None
) -> dict[str, Any]:
    body = None
    req_headers = {"Accept": "application/json", "User-Agent": "aesthetic-os-staff-oauth"}
    if headers:
        req_headers.update(headers)
    if data is not None:
        body = urlencode(data).encode("utf-8")
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(url, data=body, headers=req_headers, method=method.upper())
    try:
        with urlopen(request, timeout=8) as response:  # noqa: S310  # nosec B310 — HTTPS IdP URLs from settings only
            raw = response.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001 — never leak provider transport detail
        logger.warning("staff_oauth_http_failed provider_transport=1")
        raise StaffOAuthError("oauth_http_failed") from exc
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise StaffOAuthError("oauth_json_failed") from exc
    if not isinstance(payload, dict):
        raise StaffOAuthError("oauth_payload_invalid")
    return payload


def exchange_authorization_code(provider: str, code: str) -> dict[str, Any]:
    token_url = oauth_setting(provider, "TOKEN_URL")
    payload = _http_json(
        "POST",
        token_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": oauth_setting(provider, "REDIRECT_URI"),
            "client_id": oauth_setting(provider, "CLIENT_ID"),
            "client_secret": oauth_setting(provider, "CLIENT_SECRET"),
        },
    )
    if not payload.get("access_token") and not payload.get("id_token"):
        raise StaffOAuthError("oauth_token_missing")
    return payload


def email_from_id_token(id_token: str, *, provider: str) -> str:
    try:
        import jwt
    except ImportError as exc:  # pragma: no cover
        raise StaffOAuthError("oauth_jwt_unavailable") from exc

    client_id = oauth_setting(provider, "CLIENT_ID")
    try:
        # Signature verification requires rotating JWKS; claim checks after HTTPS token
        # exchange still bind aud/iss to our client. Fail closed on mismatch.
        claims = jwt.decode(
            id_token,
            options={"verify_signature": False, "verify_aud": False, "verify_iss": False},
            algorithms=["RS256", "ES256"],
        )
    except Exception as exc:  # noqa: BLE001
        raise StaffOAuthError("oauth_id_token_invalid") from exc

    if not isinstance(claims, dict):
        raise StaffOAuthError("oauth_id_token_invalid")
    iss = str(claims.get("iss") or "")
    allowed_iss = {
        "google": {"https://accounts.google.com", "accounts.google.com"},
        "apple": {"https://appleid.apple.com"},
    }.get(provider, set())
    if allowed_iss and iss not in allowed_iss:
        raise StaffOAuthError("oauth_iss_mismatch")
    aud = claims.get("aud")
    aud_values = aud if isinstance(aud, list) else [aud]
    if client_id and client_id not in {str(value) for value in aud_values if value}:
        raise StaffOAuthError("oauth_aud_mismatch")

    email = str(claims.get("email") or "").strip().lower()
    email_verified = claims.get("email_verified", True)
    if not email or "@" not in email:
        raise StaffOAuthError("oauth_email_missing")
    if email_verified is False or email_verified == "false":
        raise StaffOAuthError("oauth_email_unverified")
    return email


def email_from_google_userinfo(access_token: str) -> str:
    userinfo_url = oauth_setting("google", "USERINFO_URL", "https://openidconnect.googleapis.com/v1/userinfo")
    payload = _http_json(
        "GET",
        userinfo_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    email = str(payload.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise StaffOAuthError("oauth_email_missing")
    if payload.get("email_verified") is False:
        raise StaffOAuthError("oauth_email_unverified")
    return email


def resolve_provider_email(provider: str, token_payload: dict[str, Any]) -> str:
    if provider == "google":
        access_token = str(token_payload.get("access_token") or "")
        if access_token:
            return email_from_google_userinfo(access_token)
        id_token = str(token_payload.get("id_token") or "")
        return email_from_id_token(id_token, provider="google")
    if provider == "apple":
        id_token = str(token_payload.get("id_token") or "")
        return email_from_id_token(id_token, provider="apple")
    raise StaffOAuthError("oauth_provider_unknown")


def complete_staff_oauth_login(request, *, provider: str, email: str):
    """Log in only an existing active staff user. Never auto-provisions."""
    user = get_user_model().objects.filter(email__iexact=email, is_staff=True, is_active=True).first()
    if not user:
        audit_staff_event(
            StaffSecurityAudit.EventType.LOGIN_FAILURE,
            request=request,
            metadata={"provider": provider, "reason": "staff_not_provisioned"},
        )
        raise StaffOAuthError("staff_not_provisioned")

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    mark_staff_session_authenticated(request)
    clear_login_failures(email, request)
    audit_staff_event(
        StaffSecurityAudit.EventType.LOGIN_SUCCESS,
        staff_user=user,
        request=request,
        metadata={"provider": provider},
    )
    return user
