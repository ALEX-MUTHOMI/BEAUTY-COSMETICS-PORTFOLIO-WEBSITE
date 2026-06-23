import copy
import logging
import time
import uuid
from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from bookings.tests.factories import create_booking
from checkout.services import create_checkout_session
from users.services import get_redis_client

User = get_user_model()


def _scope_settings(**rates):
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"].update(rates)
    return override_settings(REST_FRAMEWORK=rest_framework)


def _clear_scope(scope):
    client = get_redis_client()
    for pattern in (f"throttle:{scope}:*", f"abuse:*:{scope}:*"):
        for key in client.scan_iter(pattern):
            client.delete(key)


def _action_values(scope):
    client = get_redis_client()
    return [client.get(key) for key in client.scan_iter(f"abuse:action:{scope}:*")]


@pytest.mark.django_db(transaction=True)
def test_invalid_booking_status_enumeration_cools_down_without_leaking_actor_or_token(caplog):
    _clear_scope("booking_status")
    client = Client()
    source_ip = "203.0.113.61"
    public_token = "00000000-0000-4000-8000-000000000001"

    caplog.set_level(logging.WARNING, logger="core.abuse")
    with override_settings(ABUSE_COOLDOWN_SCORE=4, ABUSE_COOLDOWN_SECONDS=30):
        denied = [
            client.get(
                f"/api/bookings/status/00000000-0000-4000-8000-00000000000{index}/",
                REMOTE_ADDR=source_ip,
                secure=True,
            )
            for index in range(1, 5)
        ]
        blocked = client.get(f"/api/bookings/status/{public_token}/", REMOTE_ADDR=source_ip, secure=True)

    assert [response.status_code for response in denied] == [404, 404, 404, 404]
    assert blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert int(blocked["Retry-After"]) >= 1
    assert _action_values("booking_status") == ["cooldown"]

    event_messages = [message for message in caplog.messages if "abuse_event=" in message]
    assert event_messages
    assert all(source_ip not in message and public_token not in message for message in event_messages)
    assert all("storage_key" not in message and "request_body" not in message for message in event_messages)
    assert all(source_ip not in key and public_token not in key for key in get_redis_client().scan_iter("abuse:*"))


@pytest.mark.django_db(transaction=True)
def test_ignored_retry_after_escalates_to_temporary_route_ban_but_compliant_polling_does_not():
    _clear_scope("booking_status")
    booking = create_booking()
    client = Client()

    with (
        _scope_settings(booking_status="1/min"),
        override_settings(
            ABUSE_COOLDOWN_SCORE=4,
            ABUSE_TEMPORARY_BAN_SCORE=6,
            ABUSE_WAF_CANDIDATE_SCORE=8,
            ABUSE_COOLDOWN_SECONDS=30,
            ABUSE_TEMPORARY_BAN_SECONDS=30,
        ),
    ):
        first = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)
        limited = [client.get(f"/api/bookings/status/{booking.public_id}/", secure=True) for _ in range(4)]
        escalated = client.get(f"/api/bookings/status/{booking.public_id}/", secure=True)

    assert first.status_code == status.HTTP_200_OK
    assert all(response.status_code == status.HTTP_429_TOO_MANY_REQUESTS for response in limited)
    assert all(response.json() == {"detail": "Too many requests. Please try again later."} for response in limited)
    assert escalated.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert int(escalated["Retry-After"]) >= 1
    assert _action_values("booking_status") == ["temporary_ban"]

    _clear_scope("booking_status")
    with _scope_settings(booking_status="1/min"):
        compliant = Client()
        assert (
            compliant.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code == status.HTTP_200_OK
        )
        one_limit = compliant.get(f"/api/bookings/status/{booking.public_id}/", secure=True)

    assert one_limit.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert _action_values("booking_status") == []


@pytest.mark.django_db(transaction=True)
def test_expired_cooldown_and_authenticated_actor_isolation_are_preserved():
    _clear_scope("booking_status")
    booking = create_booking()
    client = Client()
    with override_settings(ABUSE_SCORE_WINDOW_SECONDS=1, ABUSE_COOLDOWN_SCORE=4, ABUSE_COOLDOWN_SECONDS=1):
        for index in range(1, 5):
            assert (
                client.get(f"/api/bookings/status/00000000-0000-4000-8000-00000000000{index}/", secure=True).status_code
                == status.HTTP_404_NOT_FOUND
            )
        assert (
            client.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code
            == status.HTTP_429_TOO_MANY_REQUESTS
        )
        time.sleep(1.2)
        assert client.get(f"/api/bookings/status/{booking.public_id}/", secure=True).status_code == status.HTTP_200_OK

    _clear_scope("checkout_detail")
    owner = User.objects.create_user(email="abuse-owner@beauty.test", phone_number="+254712781001")
    other = User.objects.create_user(email="abuse-other@beauty.test", phone_number="+254712781002")
    checkout = create_checkout_session(
        owner,
        Decimal("100.00"),
        "KES",
        "Actor isolation",
        "booking_candidate",
        "abuse-actor-isolation",
        "abuse-actor-isolation-session",
    )
    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    other_client = APIClient()
    other_client.force_authenticate(user=other)
    shared_ip = "203.0.113.62"
    missing_checkout = uuid.UUID("00000000-0000-4000-8000-000000000099")

    with override_settings(ABUSE_COOLDOWN_SCORE=4, ABUSE_COOLDOWN_SECONDS=30):
        assert (
            owner_client.get(
                f"/api/checkout/sessions/{missing_checkout}/", REMOTE_ADDR=shared_ip, secure=True
            ).status_code
            == 404
        )
        assert (
            owner_client.get(
                f"/api/checkout/sessions/{missing_checkout}/", REMOTE_ADDR=shared_ip, secure=True
            ).status_code
            == 404
        )
        assert (
            owner_client.get(
                f"/api/checkout/sessions/{missing_checkout}/", REMOTE_ADDR=shared_ip, secure=True
            ).status_code
            == 429
        )
        other_response = other_client.get(f"/api/checkout/sessions/{checkout.id}/", REMOTE_ADDR=shared_ip, secure=True)

    assert other_response.status_code == status.HTTP_404_NOT_FOUND
