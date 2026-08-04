"""Logging filters that keep request-scoped identifiers and PII out of console output."""

import logging

from core.sentry_scrubber import scrub_pii_text


class RequestPathRedactionFilter(logging.Filter):
    """Replace Django request-log paths with a stable route name."""

    def filter(self, record):
        request = getattr(record, "request", None)
        if request is None:
            return True

        match = getattr(request, "resolver_match", None)
        route = getattr(match, "view_name", None) or "unresolved"
        status_code = getattr(record, "status_code", None)
        if status_code is None:
            status_code = getattr(getattr(record, "response", None), "status_code", "unknown")

        record.msg = "http_request status=%s route=%s"
        record.args = (status_code, route)
        return True


class PiiMessageRedactionFilter(logging.Filter):
    """Scrub email / Kenyan MSISDN / tokenish secrets from log messages (DPA/GDPR)."""

    def filter(self, record):
        try:
            message = record.getMessage()
            scrubbed = scrub_pii_text(message)
            if scrubbed != message:
                record.msg = scrubbed
                record.args = ()
        except Exception:  # noqa: BLE001 — never break logging
            return True
        return True
