from unittest.mock import patch

from billing.tasks import dlq_billing


def test_billing_dlq_task_logs_only_redacted_payload_and_correlation():
    payload = {
        "phone_number": "+254712345678",
        "CheckoutRequestID": "provider-request-reference",
        "nested": {"access_token": "provider-access-token"},
    }

    with patch("billing.tasks.logger.critical") as mocked_log:
        assert dlq_billing.run(payload, "test reason", "request-correlation") is True

    rendered = " ".join(str(item) for item in mocked_log.call_args.args)
    assert "+254712345678" not in rendered
    assert "provider-request-reference" not in rendered
    assert "provider-access-token" not in rendered
    assert "request-correlation" not in rendered
