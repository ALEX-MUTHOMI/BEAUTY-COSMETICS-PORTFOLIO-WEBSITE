import logging
from types import SimpleNamespace

import pytest
from django.test import Client, override_settings
from rest_framework import status

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import staff_contact_url
from users.services import get_redis_client


def _clear_scope(scope):
    client = get_redis_client()
    for pattern in (f"throttle:{scope}:*", f"abuse:*:{scope}:*"):
        for key in client.scan_iter(pattern):
            client.delete(key)


def _action_values(scope):
    client = get_redis_client()
    return [client.get(key) for key in client.scan_iter(f"abuse:action:{scope}:*")]


@pytest.mark.django_db(transaction=True)
def test_staff_contact_probe_is_scored_then_blocked_before_permission_work():
    _clear_scope("staff_contact_reveal")
    booking = create_booking()
    client = Client()

    with override_settings(ABUSE_COOLDOWN_SCORE=4, ABUSE_COOLDOWN_SECONDS=30):
        denied = client.post(staff_contact_url(booking), {"reason": "probe"}, secure=True)
        blocked = client.post(staff_contact_url(booking), {"reason": "probe"}, secure=True)

    assert denied.status_code == status.HTTP_403_FORBIDDEN
    assert blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert _action_values("staff_contact_reveal") == ["cooldown"]
    assert b"phone" not in blocked.content.lower()
    assert b"email" not in blocked.content.lower()


@pytest.mark.django_db(transaction=True)
def test_raw_storage_and_rejected_webhook_signals_are_redacted_and_ttl_bound(caplog):
    _clear_scope("media_resolver")
    _clear_scope("webhook")
    client = Client()
    raw_path_marker = "private/customer/grace@example.test/original.jpg"
    rejected_source = "203.0.113.63"
    caplog.set_level(logging.WARNING, logger="core.abuse")

    with override_settings(ABUSE_COOLDOWN_SCORE=4, ABUSE_COOLDOWN_SECONDS=30):
        raw_path = client.get(f"/media/{raw_path_marker}", REMOTE_ADDR=rejected_source, secure=True)
    with override_settings(ABUSE_COOLDOWN_SCORE=5, ABUSE_COOLDOWN_SECONDS=30):
        rejected_webhook = client.post(
            "/api/checkout/mpesa/webhook/",
            data="{}",
            content_type="application/json",
            REMOTE_ADDR=rejected_source,
            secure=True,
        )

    assert raw_path.status_code == status.HTTP_404_NOT_FOUND
    assert rejected_webhook.status_code == status.HTTP_403_FORBIDDEN
    assert _action_values("media_resolver") == ["cooldown"]
    assert _action_values("webhook") == ["cooldown"]
    messages = [message for message in caplog.messages if "abuse_event=" in message]
    assert len(messages) >= 2
    assert all(raw_path_marker not in message and rejected_source not in message for message in messages)
    assert all("storage_key" not in message and "request_body" not in message for message in messages)
    assert all(
        raw_path_marker not in key and rejected_source not in key for key in get_redis_client().scan_iter("abuse:*")
    )


@pytest.mark.django_db(transaction=True)
def test_booking_hold_fails_closed_and_generic_when_redis_admission_is_unavailable(monkeypatch):
    class BrokenRedis:
        def eval(self, *_args):
            raise ConnectionError("redis unavailable")

    # Replace only the throttle module reference. Patching users.services itself
    # would leak the fake client into the autouse Redis cleanup fixture.
    monkeypatch.setattr(
        "core.throttling.services",
        SimpleNamespace(get_redis_client=lambda: BrokenRedis()),
    )
    response = Client().post("/api/bookings/holds/", data="{}", content_type="application/json", secure=True)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "Service temporarily unavailable."}
    assert b"redis" not in response.content.lower()
    assert b"traceback" not in response.content.lower()
