import pytest
from django.apps import apps
from django.test import Client

from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_reset_token_hash_cannot_be_used_as_password_reset_token():
    staff = make_staff()

    from bookings.services.staff_auth import STAFF_PASSWORD_RESET_OUTBOX

    STAFF_PASSWORD_RESET_OUTBOX.clear()
    Client().post(
        "/api/staff/auth/password-reset/request/",
        {"email": staff.email},
        content_type="application/json",
        secure=True,
    )
    challenge_model = apps.get_model("bookings", "StaffPasswordResetChallenge")
    challenge = challenge_model.objects.get(staff_user=staff)

    response = Client().post(
        "/api/staff/auth/password-reset/confirm/",
        {"token": challenge.token_hash_hmac, "new_password": "Hash replay secure phrase 2026"},
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 400
    staff.refresh_from_db()
    assert not staff.check_password("Hash replay secure phrase 2026")
