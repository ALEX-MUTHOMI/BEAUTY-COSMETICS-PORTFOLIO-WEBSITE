from datetime import timedelta

import pytest
from django.apps import apps
from django.test import Client
from django.utils import timezone

from bookings.infrastructure.email_provider import reset_fake_email_outbox
from bookings.services.staff_auth import harvest_staff_password_reset_token_for_tests
from bookings.tests.test_staff_auth_helpers import make_customer, make_staff


@pytest.fixture(autouse=True)
def _clear_fake_email_outbox():
    reset_fake_email_outbox()
    yield
    reset_fake_email_outbox()


@pytest.mark.django_db
def test_staff_password_reset_request_is_generic_and_stores_hashed_token_only():
    staff = make_staff()
    make_customer()

    existing = Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": staff.email},
        content_type="application/json",
        secure=True,
    )
    unknown = Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": "missing-staff@example.com"},
        content_type="application/json",
        secure=True,
    )
    customer = Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": "staff-auth-customer@example.com"},
        content_type="application/json",
        secure=True,
    )

    assert existing.status_code == unknown.status_code == customer.status_code == 200
    assert existing.json() == unknown.json() == customer.json()
    raw_token = harvest_staff_password_reset_token_for_tests()
    assert raw_token

    challenge_model = apps.get_model("bookings", "StaffPasswordResetChallenge")
    challenge = challenge_model.objects.get(staff_user=staff)
    assert raw_token not in challenge.token_hash_hmac
    assert challenge.status == "pending"


@pytest.mark.django_db
def test_staff_password_reset_confirm_expires_is_single_use_and_invalidates_old_session():
    staff = make_staff()
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            {"email": staff.email, "password": "Correct horse battery staple 2026"},
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": staff.email},
        content_type="application/json",
        secure=True,
    )
    token = harvest_staff_password_reset_token_for_tests()
    new_password = "Nairobi secure staff reset phrase 2026"

    confirm = Client().post(
        "/api/staff/auth/password-reset/confirm/",
        {"token": token, "new_password": new_password},
        content_type="application/json",
        secure=True,
    )
    reuse = Client().post(
        "/api/staff/auth/password-reset/confirm/",
        {"token": token, "new_password": "Another secure reset phrase 2026"},
        content_type="application/json",
        secure=True,
    )

    assert confirm.status_code == 200
    assert reuse.status_code == 400
    assert client.get("/api/staff/auth/me/", secure=True).status_code == 403

    staff.refresh_from_db()
    assert staff.check_password(new_password)

    reset_fake_email_outbox()
    Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": staff.email},
        content_type="application/json",
        secure=True,
    )
    expired_token = harvest_staff_password_reset_token_for_tests()
    challenge_model = apps.get_model("bookings", "StaffPasswordResetChallenge")
    challenge = challenge_model.objects.order_by("-created_at").first()
    challenge.expires_at = timezone.now() - timedelta(minutes=1)
    challenge.save(update_fields=["expires_at", "updated_at"])

    expired = Client().post(
        "/api/staff/auth/password-reset/confirm/",
        {"token": expired_token, "new_password": "Expired token secure phrase 2026"},
        content_type="application/json",
        secure=True,
    )
    assert expired.status_code == 400
