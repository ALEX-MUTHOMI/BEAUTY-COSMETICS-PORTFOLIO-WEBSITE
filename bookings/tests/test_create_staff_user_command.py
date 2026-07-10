import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
def test_create_staff_user_command_grants_portal_permissions(capsys):
    call_command(
        "create_staff_user",
        email="portal-owner@example.com",
        password="Nairobi salon passphrase secure 2026!",
        display_name="Portal Owner",
    )
    user = get_user_model().objects.get(email="portal-owner@example.com")
    assert user.is_staff is True
    assert user.has_perm("bookings.view_staff_portal")
    assert user.has_perm("bookings.view_staff_booking")
    assert user.has_perm("bookings.view_staff_contact_details")
    assert user.has_perm("bookings.view_staff_payment_summary")
    out = capsys.readouterr().out
    assert "/staff/login" in out
    assert "/staff/dashboard" in out


@pytest.mark.django_db
def test_create_staff_user_rejects_weak_password():
    with pytest.raises(CommandError, match="15 characters"):
        call_command(
            "create_staff_user",
            email="weak@example.com",
            password="short",
        )


@pytest.mark.django_db
def test_staff_profile_next_path_is_dashboard():
    from bookings.services.staff_auth import staff_profile
    from bookings.tests.test_staff_portal_helpers import make_staff_user

    profile = staff_profile(make_staff_user(permissions=["view_staff_portal"]))
    assert profile["next"] == "/staff/dashboard"
