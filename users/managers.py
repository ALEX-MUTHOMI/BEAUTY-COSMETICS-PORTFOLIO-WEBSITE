from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomUserQuerySet(models.QuerySet):
    """
    Custom QuerySet to support active filtering and soft-delete capabilities.
    """

    def alive(self):
        """Return only records that have not been soft-deleted."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only soft-deleted records."""
        return self.filter(is_deleted=True)


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model where email is the unique identifier
    for authentication instead of usernames, and soft-deleted rows are filtered out by default.
    """

    def get_queryset(self):
        """
        By default, all queries (all(), filter(), etc.) filter out soft-deleted rows,
        protecting active business queries from exposing anonymized/deleted entities.
        """
        return CustomUserQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        """
        Explicit method to bypass the default soft-delete filter when auditing logs
        or financial transactions linked to anonymized accounts.
        """
        return CustomUserQuerySet(self.model, using=self._db)

    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        """
        Create and save a standard CustomUser with an email, optional phone number, and optional password.
        """
        if not email:
            raise ValueError("The Email field must be set.")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_otp_verified", False)

        user = self.model(email=email, phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number=None, password=None, **extra_fields):
        """
        Create and save a CustomUser superuser with administrative privileges.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_otp_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, phone_number, password, **extra_fields)
