import copy
from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session
from checkout.throttles import CheckoutSessionCreateThrottle, CheckoutSessionDetailThrottle
from users.services import get_redis_client

User = get_user_model()


def _scope_settings(**rates):
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"].update(rates)
    return override_settings(REST_FRAMEWORK=rest_framework)


def _clear_scope(scope):
    client = get_redis_client()
    for key in client.scan_iter(f"throttle:{scope}:*"):
        client.delete(key)


@pytest.mark.django_db(transaction=True)
def test_csrf_bootstrap_throttle_is_generic_and_actor_isolated():
    _clear_scope("csrf_bootstrap")
    with _scope_settings(csrf_bootstrap="1/min"):
        client = Client()
        first = client.get("/api/csrf/", REMOTE_ADDR="203.0.113.10", secure=True)
        blocked = client.get("/api/csrf/", REMOTE_ADDR="203.0.113.10", secure=True)
        other_actor = client.get("/api/csrf/", REMOTE_ADDR="203.0.113.11", secure=True)

    assert first.status_code == 200
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert "Retry-After" in blocked
    assert other_actor.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_booking_hold_malformed_pressure_is_throttled_without_reflection():
    _clear_scope("booking_hold")
    with _scope_settings(booking_hold="1/min"):
        client = Client()
        first = client.post("/api/bookings/holds/", data="{", content_type="application/json", secure=True)
        blocked = client.post("/api/bookings/holds/", data="{", content_type="application/json", secure=True)

    assert first.status_code == 400
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert all(marker not in blocked.content.lower() for marker in (b"token", b"storage", b"provider", b"traceback"))


@pytest.mark.django_db(transaction=True)
def test_public_gallery_and_media_admission_controls_are_bounded():
    _clear_scope("public_gallery")
    _clear_scope("media_resolver")
    with _scope_settings(public_gallery="1/min", media_resolver="1/min"):
        client = Client()
        assert client.get("/api/gallery/public/homepage/", secure=True).status_code == 200
        blocked_gallery = client.get("/api/gallery/public/homepage/", secure=True)
        first_media = client.get("/media/public/00000000-0000-4000-8000-000000000000.webp", secure=True)
        blocked_media = client.get("/media/public/00000000-0000-4000-8000-000000000000.webp", secure=True)

    assert blocked_gallery.status_code == 429
    assert first_media.status_code == 404
    assert blocked_media.status_code == 429
    assert b"storage" not in blocked_media.content.lower()


@pytest.mark.django_db(transaction=True)
def test_contact_reveal_pressure_is_limited_before_permission_processing():
    _clear_scope("staff_contact_reveal")
    with _scope_settings(staff_contact_reveal="1/min"):
        client = Client()
        first = client.post("/api/staff/bookings/00000000-0000-4000-8000-000000000000/contact-access/", secure=True)
        blocked = client.post("/api/staff/bookings/00000000-0000-4000-8000-000000000000/contact-access/", secure=True)

    assert first.status_code == 403
    assert blocked.status_code == 429
    assert b"phone" not in blocked.content.lower()
    assert b"email" not in blocked.content.lower()


@pytest.mark.django_db(transaction=True)
def test_checkout_detail_throttle_is_customer_scoped_and_restores_production_rate():
    _clear_scope("checkout_detail")
    owner = User.objects.create_user(email="checkout-detail-owner@aesthetic-os.test", phone_number="+254712780011")
    attacker = User.objects.create_user(
        email="checkout-detail-attacker@aesthetic-os.test", phone_number="+254712780012"
    )
    checkout = create_checkout_session(
        owner,
        Decimal("100.00"),
        "KES",
        "Throttle detail",
        "booking_candidate",
        "checkout-detail-pressure",
        "checkout-detail-pressure-session",
    )
    with _scope_settings(checkout_detail="1/min"):
        owner_client = APIClient()
        owner_client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        owner_client.force_authenticate(user=owner)
        attacker_client = APIClient()
        attacker_client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        attacker_client.force_authenticate(user=attacker)

        first = owner_client.get(f"/api/checkout/sessions/{checkout.id}/")
        blocked = owner_client.get(f"/api/checkout/sessions/{checkout.id}/")
        other_actor = attacker_client.get(f"/api/checkout/sessions/{checkout.id}/")

    assert first.status_code == status.HTTP_200_OK
    assert blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked.json() == {"detail": "Too many requests. Please try again later."}
    assert "Retry-After" in blocked
    assert other_actor.status_code == status.HTTP_404_NOT_FOUND
    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["checkout_detail"] == "60/min"


def test_checkout_route_classes_use_explicit_scopes():
    assert CheckoutSessionCreateThrottle.scope == "checkout_create"
    assert CheckoutSessionDetailThrottle.scope == "checkout_detail"
