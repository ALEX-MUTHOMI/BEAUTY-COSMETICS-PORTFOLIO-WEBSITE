"""Optional Sentry SDK bootstrap — no-op unless SENTRY_DSN is configured."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("core.sentry")


def init_sentry() -> bool:
    dsn = (os.environ.get("SENTRY_DSN") or "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        from core.sentry_scrubber import scrub_sentry_event

        def _before_send(event, _hint):
            return scrub_sentry_event(event)

        sentry_sdk.init(
            dsn=dsn,
            integrations=[DjangoIntegration()],
            send_default_pii=False,
            before_send=_before_send,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
        )
        logger.info("sentry_initialized=true")
        return True
    except Exception:  # noqa: BLE001 — never block boot for missing optional SDK
        logger.warning("sentry_initialized=false")
        return False
