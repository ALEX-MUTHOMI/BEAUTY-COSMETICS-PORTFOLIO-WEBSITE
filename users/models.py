import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from core.models import AuditMixin
from users.managers import CustomUserManager

# Strict Kenyan Phone Number Regular Expression (Safaricom / Airtel / Telkom)
# Matches 07XXXXXXXX, 01XXXXXXXX, 2547XXXXXXXX, +2547XXXXXXXX, 2541XXXXXXXX, etc.
# Crucial for routing M-Pesa STK push billing APIs cleanly.
KENYAN_PHONE_REGEX = RegexValidator(
    regex=r"^(?:254|\+254|0)?([71]\d{8})$",
    message="Phone number must be a valid Kenyan format (e.g. +254712345678 or 0712345678).",
)


class CustomUser(AbstractBaseUser, PermissionsMixin, AuditMixin):
    """
    Production-grade Custom User Authentication Model.
    - Uses Email as the unique username credential.
    - Integrates abstract UUID auditing and soft-deletion capability.
    - Validates Kenyan phone number patterns required for M-Pesa payments.
    - Implements GDPR anonymization compliance.
    """

    email = models.EmailField(
        unique=True,
        max_length=255,
        help_text="Primary email credential utilized for authentication.",
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[KENYAN_PHONE_REGEX],
        null=True,
        blank=True,
        help_text="Kenyan phone number required for routing M-Pesa STK billing pushes.",
    )
    is_otp_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the user has validated their active OTP phone/email session.",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the Django administrative panel.",
    )
    is_active = models.BooleanField(
        default=True, help_text="Designates whether this user account is active."
    )
    gdpr_consent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the user consented to GDPR Article 7 data privacy terms.",
    )
    terms_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the user accepted platform Terms & Conditions.",
    )

    # Register custom authentication manager
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = "beauty_users"

    def __str__(self):
        return self.email

    def anonymize(self):
        """
        Irreversibly scrubs Personal Identifiable Information (PII) to comply
        with GDPR Article 17 ('Right to be Forgotten').
        - Sets is_active=False and is_deleted=True.
        - Wipes password hash completely.
        - Scrambles email and phone fields with randomized non-identifiable hashes.
        - Preserves the primary key (UUID) to keep M-Pesa ledger transactions consistent.
        """
        random_suffix = uuid.uuid4().hex[:12]
        self.email = f"anonymized-{random_suffix}@forgotten.beauty.com"
        self.phone_number = "+254000000000"  # Safe dummy Kenyan non-routable format
        self.is_active = False
        self.is_deleted = True
        self.is_otp_verified = False
        self.gdpr_consent_at = None
        self.terms_accepted_at = None
        self.set_unusable_password()
        self.save()
