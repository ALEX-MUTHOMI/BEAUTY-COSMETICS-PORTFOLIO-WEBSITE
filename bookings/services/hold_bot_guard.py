"""Server-side bot gate for public hold creation under abuse pressure."""

from __future__ import annotations

import logging

from django.core.exceptions import ValidationError

from bookings.domain.circuit_breaker import BookingCircuitBreaker
from bookings.models import BookingPolicy
from users.services import OTPService

logger = logging.getLogger("bookings.hold_bot_guard")

GENERIC_HOLD_BOT_ERROR = "Booking request could not be accepted."


def _policy() -> BookingPolicy:
    return BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()


def require_hold_turnstile_if_abused(*, request, payload, redis_client) -> None:
    """
    Enforce Cloudflare Turnstile when the booking circuit is elevated/abused.

    Client-only Turnstile is not a security boundary. Under ABUSE/LOCKDOWN
    (and ELEVATED when policy.require_turnstile_under_abuse is true), the hold
    endpoint must verify the token server-side before capacity is consumed.
    """
    policy = _policy()
    if not policy.require_turnstile_under_abuse:
        return

    mode = (
        BookingCircuitBreaker(redis_client).mode_for_context() if redis_client else BookingCircuitBreaker.Mode.LOCKDOWN
    )
    if mode == BookingCircuitBreaker.Mode.NORMAL:
        return

    token = str((payload or {}).get("turnstile_token") or "").strip()
    remote_ip = request.META.get("REMOTE_ADDR", "")
    if not token or not OTPService.verify_turnstile_token(token, remote_ip=remote_ip or None):
        logger.info(
            "booking.hold.turnstile_rejected",
            extra={"circuit_mode": mode, "has_token": bool(token)},
        )
        raise ValidationError(GENERIC_HOLD_BOT_ERROR)
