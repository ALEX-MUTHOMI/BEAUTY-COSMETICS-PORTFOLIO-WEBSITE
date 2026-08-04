"""Unit proofs for console PII redaction filter (GDPR / Kenya DPA)."""

import logging

from core.logging_filters import PiiMessageRedactionFilter


def test_pii_message_redaction_filter_scrubs_email_and_msisdn():
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="customer grace@example.com dialed +254712345678",
        args=(),
        exc_info=None,
    )
    assert PiiMessageRedactionFilter().filter(record) is True
    assert "grace@example.com" not in record.getMessage()
    assert "+254712345678" not in record.getMessage()
    assert "[REDACTED]" in record.getMessage()
