"""PII / secret scrubbers for optional Sentry (GDPR + Kenya DPA 2019)."""

from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

_EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
_MSISDN_RE = re.compile(r"(?:\+?254|0)7\d{8}\b")
_TOKENISH_RE = re.compile(
    r"(?:csrf|csrftoken|turnstile|idempotency|access_token|authorization|bearer|sessionid)" r"[=:\s]+[^\s\"',}]+",
    re.I,
)
_SENSITIVE_KEYS = (
    "email",
    "phone",
    "msisdn",
    "password",
    "token",
    "secret",
    "authorization",
    "cookie",
    "idempotency",
)


def scrub_pii_text(value: str) -> str:
    text = _EMAIL_RE.sub(REDACTED, value)
    text = _MSISDN_RE.sub(REDACTED, text)

    def _token_sub(match: re.Match[str]) -> str:
        key = re.split(r"[=:\s]", match.group(0), maxsplit=1)[0]
        return f"{key}={REDACTED}"

    return _TOKENISH_RE.sub(_token_sub, text)


def scrub_unknown(value: Any, depth: int = 0) -> Any:
    if depth > 6:
        return REDACTED
    if isinstance(value, str):
        return scrub_pii_text(value)
    if isinstance(value, list):
        return [scrub_unknown(item, depth + 1) for item in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, nested in value.items():
            lower = str(key).lower()
            if any(marker in lower for marker in _SENSITIVE_KEYS):
                out[str(key)] = REDACTED
            else:
                out[str(key)] = scrub_unknown(nested, depth + 1)
        return out
    return value


def scrub_sentry_event(event: dict[str, Any] | None) -> dict[str, Any] | None:
    if not event:
        return None
    try:
        return scrub_unknown(dict(event))
    except Exception:  # noqa: BLE001 — fail closed for observability
        return None
