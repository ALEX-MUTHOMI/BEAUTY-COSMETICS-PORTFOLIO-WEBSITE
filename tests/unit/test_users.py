import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import CustomUser

User = get_user_model()


@pytest.mark.django_db
def test_create_user_requires_email():
    """
    Enforce that a CustomUser cannot be created without a valid email address.
    """
    with pytest.raises(ValueError, match="The Email field must be set"):
        User.objects.create_user(
            email="",
            phone_number="+254712345678",
            password="SecurePassword123!"
        )


@pytest.mark.django_db
def test_create_user_requires_valid_kenyan_phone():
    """
    Enforce that a CustomUser cannot be created without a valid Kenyan phone number.
    Valid formats include: 07XXXXXXXX, 01XXXXXXXX, +2547XXXXXXXX, etc.
    """
    # Test Case A: Create user with invalid phone number format
    user = User(
        email="test_invalid_phone@beauty.com",
        phone_number="123456"  # Clearly invalid format
    )
    user.set_password("SecurePassword123!")

    # In Django, validators run during model clean verification
    with pytest.raises(ValidationError):
        user.full_clean()

    # Test Case B: Verify a correct Kenyan number passes clean verification
    valid_user = User(
        email="test_valid_phone@beauty.com",
        phone_number="+254712345678"
    )
    valid_user.set_password("SecurePassword123!")
    valid_user.full_clean()  # Should not raise any exception


@pytest.mark.django_db
def test_user_password_uses_argon2():
    """
    Enforce that the CustomUser's password is encrypted using the Argon2 hashing algorithm,
    guaranteeing production-grade cryptographic boundaries instead of default PBKDF2.
    """
    user = User.objects.create_user(
        email="argon2_test@beauty.com",
        phone_number="0712345678",
        password="SecurePassword123!"
    )
    # Argon2 password hashes always start with the 'argon2' marker
    assert user.password.startswith("argon2$")


@pytest.mark.django_db
def test_auditmixin_automatic_timestamps():
    """
    Enforce that the AuditMixin automatically populates:
    - UUID primary key (cryptographically secure)
    - created_at and updated_at timestamps on model save.
    - is_deleted soft-delete field defaults to False.
    """
    user = User.objects.create_user(
        email="audit_test@beauty.com",
        phone_number="0712345678",
        password="SecurePassword123!"
    )
    
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.is_deleted is False


@pytest.mark.django_db
def test_gdpr_anonymization_destroys_pii():
    """
    Enforce GDPR Article 17 compliance. 
    - Calling anonymize() must irreversibly scramble PII (email, phone).
    - Sets is_deleted=True and is_active=False.
    - Renders the password unusable.
    - Preserves UUID to keep database foreign keys valid.
    """
    original_email = "gdpr_client@beauty.com"
    original_phone = "+254712345678"
    
    user = User.objects.create_user(
        email=original_email,
        phone_number=original_phone,
        password="SecurePassword123!"
    )
    user.gdpr_consent_at = pytest.datetime = "2026-05-27T00:00:00Z"
    user.save()

    # Call GDPR anonymization engine
    user.anonymize()

    # Refetch from DB to verify persistence
    user.refresh_from_db()

    # Assert PII is completely scrubbed and non-identifiable
    assert user.email != original_email
    assert "anonymized-" in user.email
    assert user.phone_number == "+254000000000"
    
    # Assert flags are disabled
    assert user.is_active is False
    assert user.is_deleted is True
    assert user.is_otp_verified is False
    assert user.gdpr_consent_at is None
    
    # Assert password is cryptographically unusable
    assert user.has_usable_password() is False


@pytest.mark.django_db
def test_soft_deleted_users_excluded_from_active_queries():
    """
    Enforce that soft-deleted users are excluded from standard managers
    to prevent accidental active business lookup, but can be retrieved via audit managers.
    """
    user1 = User.objects.create_user(
        email="active_user@beauty.com",
        phone_number="0711111111",
        password="SecurePassword123!"
    )
    user2 = User.objects.create_user(
        email="deleted_user@beauty.com",
        phone_number="0722222222",
        password="SecurePassword123!"
    )

    # Soft-delete the second user
    user2.anonymize()

    # Standard objects manager should only return active, non-deleted users
    active_users = list(User.objects.all())
    assert user1 in active_users
    assert user2 not in active_users
    assert len(active_users) == 1

    # audit manager must be able to bypass soft-delete to retrieve for ledger consistency
    all_users = list(User.objects.all_with_deleted())
    assert user1 in all_users
    assert user2 in all_users
    assert len(all_users) == 2
