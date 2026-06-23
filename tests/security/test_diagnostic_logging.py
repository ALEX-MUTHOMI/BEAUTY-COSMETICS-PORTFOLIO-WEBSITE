import copy
import logging

import pytest
from django.conf import settings
from django.test import Client, override_settings


@pytest.mark.django_db
@override_settings(BEAUTY_DIAGNOSTIC_TRACE=True)
def test_diagnostic_request_and_throttle_events_are_redacted(caplog):
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["csrf_bootstrap"] = "1/min"
    with override_settings(REST_FRAMEWORK=rest_framework), caplog.at_level(logging.INFO, logger="core.diagnostics"):
        client = Client()
        first = client.get(
            "/api/csrf/",
            secure=True,
            REMOTE_ADDR="203.0.113.40",
            HTTP_X_REQUEST_ID="attacker-supplied-secret",
        )
        limited = client.get("/api/csrf/", secure=True, REMOTE_ADDR="203.0.113.40")

    assert first.status_code == 200
    assert limited.status_code == 429
    assert first["X-Request-ID"] != "attacker-supplied-secret"
    diagnostics = "\n".join(record.getMessage() for record in caplog.records)
    assert "request_complete" in diagnostics
    assert '"event":"throttle_decision"' in diagnostics
    assert '"scope":"csrf_bootstrap"' in diagnostics
    assert '"failure_behavior":"limited_429"' in diagnostics
    assert "203.0.113.40" not in diagnostics
    assert "attacker-supplied-secret" not in diagnostics
    assert "csrf_token" not in diagnostics
    assert "storage_key" not in diagnostics
