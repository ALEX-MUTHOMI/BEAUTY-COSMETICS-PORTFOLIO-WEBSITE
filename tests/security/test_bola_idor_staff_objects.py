import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.utils import timezone

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import make_customer_user, make_staff_user, staff_contact_url


def _staff_session(client, user):
    client.force_login(user)
    session = client.session
    now = timezone.now().timestamp()
    session["staff_auth_at"] = now
    session["staff_last_activity_at"] = now
    session["staff_recent_auth_at"] = now
    session.save()


def _assert_denial_is_safe(response):
    body = response.content.decode("utf-8", errors="replace")
    for marker in (
        "Traceback",
        "Internal Server Error",
        "grace@example.com",
        "+254712345678",
        "phone",
        "email",
    ):
        assert marker not in body


@pytest.mark.django_db
def test_non_staff_customer_cannot_use_headers_or_query_to_access_staff_booking_detail():
    booking = create_booking()
    user = make_customer_user("phase-3b-customer@example.com")
    client = Client()
    client.force_login(user)

    response = client.get(
        f"/api/staff/bookings/{booking.public_id}/?role=admin&scope=all",
        secure=True,
        HTTP_X_ROLE="admin",
        HTTP_X_STAFF_ID="1",
        HTTP_X_FORWARDED_USER="admin",
    )

    assert response.status_code == 403
    _assert_denial_is_safe(response)


@pytest.mark.django_db
def test_inactive_staff_superuser_session_is_denied_staff_portal_access():
    booking = create_booking()
    user = make_staff_user(superuser=True)
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])
    client = Client()
    _staff_session(client, user)

    response = client.get(f"/api/staff/bookings/{booking.public_id}/", secure=True)

    assert response.status_code == 403
    _assert_denial_is_safe(response)


@pytest.mark.django_db
def test_contact_reveal_denial_does_not_leak_contact_data_for_staff_without_permission():
    booking = create_booking()
    user = make_staff_user()
    user.user_permissions.add(Permission.objects.get(codename="view_staff_portal"))
    client = Client()
    _staff_session(client, user)

    response = client.post(staff_contact_url(booking), {"reason": "test"}, secure=True)

    assert response.status_code == 403
    _assert_denial_is_safe(response)
