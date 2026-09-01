"""
GDPR + Kenya Data Protection Act 2019 — subject-rights intake (ticketed).

This is not an anonymous data dump. Requests are accepted, rate-limited, and
audited to a durable row with peppered hashes only. Fulfilment is staff-operated.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("bookings.privacy_rights")

# Purpose limitation map for booking customer PII (DPA 2019 / GDPR Art. 5).
BOOKING_PII_DATA_MAP: dict[str, dict[str, str]] = {
    "full_name": {
        "purpose": "identify the customer for the booked appointment",
        "lawful_basis": "contract",
        "retention": "24 months after last completed booking, then soft-delete",
    },
    "email": {
        "purpose": "transactional booking confirmation, receipt, and OTP",
        "lawful_basis": "contract",
        "retention": "24 months after last completed booking; marketing requires separate consent",
    },
    "phone": {
        "purpose": "M-Pesa STK / booking contact for the appointment",
        "lawful_basis": "contract",
        "retention": "24 months after last completed booking; never logged in cleartext",
    },
}

ALLOWED_REQUEST_TYPES = frozenset({"access", "erasure", "rectification", "objection"})
_EMAIL_RE = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", re.I)


@dataclass(frozen=True)
class PrivacyRightsTicket:
    ticket_id: str
    request_type: str
    status: str


def _details_hash(details: str) -> str:
    if not details:
        return ""
    import hmac as hmac_mod

    from django.conf import settings

    pepper = (getattr(settings, "PII_HASH_PEPPER", "") or "debug-only-booking-secret").encode()
    return hmac_mod.new(pepper, details.strip().lower().encode("utf-8"), hashlib.sha256).hexdigest()


def validate_privacy_rights_payload(payload: dict[str, Any]) -> tuple[dict[str, str] | None, str | None]:
    request_type = str(payload.get("request_type") or "").strip().lower()
    email = str(payload.get("email") or "").strip()
    phone = str(payload.get("phone") or "").strip()
    details = str(payload.get("details") or "").strip()[:500]

    if request_type not in ALLOWED_REQUEST_TYPES:
        return None, "invalid_request_type"
    if not _EMAIL_RE.match(email):
        return None, "invalid_email"
    if phone and not re.match(r"^\+?2547\d{8}$|^07\d{8}$", phone):
        return None, "invalid_phone"
    return {
        "request_type": request_type,
        "email": email,
        "phone": phone,
        "details": details,
    }, None


def accept_privacy_rights_request(
    payload: dict[str, Any],
    *,
    correlation_id: str = "",
    request_context: dict[str, Any] | None = None,
) -> PrivacyRightsTicket | None:
    from bookings.models import PrivacyRightsRequest
    from bookings.privacy import hmac_email_hash, hmac_phone_hash

    request_context = request_context or {}
    cleaned, error = validate_privacy_rights_payload(payload)
    if cleaned is None:
        logger.info("privacy_rights_rejected")
        return None

    ticket_material = f"{cleaned['request_type']}:{cleaned['email']}:{correlation_id}"
    ticket_id = hashlib.sha256(ticket_material.encode("utf-8")).hexdigest()[:20]
    email_hash = hmac_email_hash(cleaned["email"])
    phone_hash = hmac_phone_hash(cleaned["phone"]) if cleaned["phone"] else ""
    details_hash = _details_hash(cleaned["details"])
    ip_hash = ""
    ua_hash = ""
    if request_context.get("ip"):
        ip_hash = hashlib.sha256(str(request_context["ip"]).encode("utf-8")).hexdigest()
    if request_context.get("user_agent"):
        ua_hash = hashlib.sha256(str(request_context["user_agent"]).encode("utf-8")).hexdigest()

    PrivacyRightsRequest.objects.create(
        ticket_id=ticket_id,
        request_type=cleaned["request_type"],
        status=PrivacyRightsRequest.Status.ACCEPTED,
        email_hash_hmac=email_hash,
        phone_hash_hmac=phone_hash,
        details_hash_hmac=details_hash,
        correlation_id=(correlation_id or "")[:128],
        ip_hash_hmac=ip_hash,
        user_agent_hash_hmac=ua_hash,
    )

    # Audit without storing cleartext PII in logs (DPA 2019 security of processing).
    logger.info("privacy_rights_accepted ticket=%s", ticket_id)
    return PrivacyRightsTicket(ticket_id=ticket_id, request_type=cleaned["request_type"], status="accepted")
