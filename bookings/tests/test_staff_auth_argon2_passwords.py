import pytest
from django.conf import settings

from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_staff_passwords_use_argon2_and_do_not_store_plaintext():
    raw_password = "Correct horse battery staple 2026"
    staff = make_staff(password=raw_password)

    assert settings.PASSWORD_HASHERS[0] == "django.contrib.auth.hashers.Argon2PasswordHasher"
    assert staff.password.startswith("argon2")
    assert raw_password not in staff.password
    assert staff.check_password(raw_password)
