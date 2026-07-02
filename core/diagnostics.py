"""Opt-in, redacted diagnostics for local/test throttle investigations."""

from __future__ import annotations

import hashlib
import json
import logging

from django.conf import settings

logger = logging.getLogger("core.diagnostics")


def _hash(value: object) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def enabled() -> bool:
    return bool(getattr(settings, "AESTHETIC_OS_DIAGNOSTIC_TRACE", False))


def actor_metadata(request) -> dict[str, str]:
    user = getattr(request, "user", None)
    if getattr(user, "is_authenticated", False):
        actor_type = "staff" if getattr(user, "is_staff", False) else "customer"
        actor_value = getattr(user, "pk", "")
    elif "/webhook/" in getattr(request, "path", ""):
        actor_type = "provider"
        actor_value = request.META.get("REMOTE_ADDR", "")
    else:
        actor_type = "anonymous"
        actor_value = request.META.get("REMOTE_ADDR", "")
    return {"actor_type": actor_type, "actor_hash": _hash(actor_value)}


def emit(event: str, **fields) -> None:
    """Emit a structured event with only caller-approved, non-raw fields."""
    if not enabled():
        return
    logger.info("diagnostic=%s", json.dumps({"event": event, **fields}, sort_keys=True, separators=(",", ":")))


def request_event(request, response, latency_ms: int) -> None:
    match = getattr(request, "resolver_match", None)
    route = getattr(match, "view_name", None) or "unresolved"
    emit(
        "request_complete",
        request_id_hash=_hash(getattr(request, "correlation_id", "")),
        method=request.method,
        route=route,
        status_code=response.status_code,
        response_family=f"{response.status_code // 100}xx",
        latency_ms=latency_ms,
        retry_after=response.get("Retry-After", ""),
        **actor_metadata(request),
    )


def throttle_event(
    request,
    *,
    scope: str,
    rate: str,
    allowed: bool,
    tokens_remaining: object,
    retry_after: object,
    redis_status: str,
    failure_behavior: str,
) -> None:
    emit(
        "throttle_decision",
        request_id_hash=_hash(getattr(request, "correlation_id", "")),
        scope=scope,
        rate=rate,
        allowed=allowed,
        tokens_remaining=str(tokens_remaining),
        retry_after=str(retry_after or ""),
        redis_status=redis_status,
        failure_behavior=failure_behavior,
        **actor_metadata(request),
    )
