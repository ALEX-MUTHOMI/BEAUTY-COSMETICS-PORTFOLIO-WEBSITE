import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password",
    [
        "short-password",
        "password123456789",
        "Beauty1234567890",
        "Makeup@2025!!!!!",
        "staff-auth secure phrase",
        "beauty business 12345",
    ],
)
def test_staff_password_policy_rejects_weak_common_or_derived_passwords(password):
    from bookings.services.staff_auth import validate_staff_password

    with pytest.raises(ValueError):
        validate_staff_password(password, email="staff-auth@example.com", display_name="Beauty Business")


@pytest.mark.django_db
def test_staff_password_policy_accepts_long_passphrases_with_spaces_and_unicode():
    from bookings.services.staff_auth import validate_staff_password

    validate_staff_password("Nairobi salon passphrase secure 2026 ✨", email="owner@example.com")
