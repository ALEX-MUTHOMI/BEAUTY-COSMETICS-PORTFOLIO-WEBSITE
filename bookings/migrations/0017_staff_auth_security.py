import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookings", "0016_staff_portal_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffSecurityAudit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Cryptographically secure unique identifier.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        editable=False,
                        help_text="Timestamp when the database record was initialized.",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, help_text="Timestamp when the database record was last saved."),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("login_success", "Login Success"),
                            ("login_failure", "Login Failure"),
                            ("login_rate_limited", "Login Rate Limited"),
                            ("logout", "Logout"),
                            ("session_expired", "Session Expired"),
                            ("password_reset_requested", "Password Reset Requested"),
                            ("password_reset_completed", "Password Reset Completed"),
                            ("reauth_success", "Reauth Success"),
                            ("reauth_failure", "Reauth Failure"),
                            ("contact_reveal", "Contact Reveal"),
                            ("permission_denied", "Permission Denied"),
                        ],
                        max_length=64,
                    ),
                ),
                ("ip_hash_hmac", models.CharField(blank=True, max_length=128)),
                ("user_agent_hash_hmac", models.CharField(blank=True, max_length=128)),
                ("metadata_redacted", models.JSONField(blank=True, default=dict)),
                (
                    "staff_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="staff_security_audits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "booking_staff_security_audits",
            },
        ),
        migrations.CreateModel(
            name="StaffPasswordResetChallenge",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Cryptographically secure unique identifier.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        editable=False,
                        help_text="Timestamp when the database record was initialized.",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, help_text="Timestamp when the database record was last saved."),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("email_hash_hmac", models.CharField(db_index=True, max_length=128)),
                ("token_hash_hmac", models.CharField(max_length=128, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("used", "Used"),
                            ("expired", "Expired"),
                            ("revoked", "Revoked"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("ip_hash_hmac", models.CharField(blank=True, max_length=128)),
                ("user_agent_hash_hmac", models.CharField(blank=True, max_length=128)),
                (
                    "staff_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="staff_password_reset_challenges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "booking_staff_password_reset_challenges",
            },
        ),
        migrations.AddIndex(
            model_name="staffsecurityaudit",
            index=models.Index(fields=["event_type", "created_at"], name="staff_sec_event_time_idx"),
        ),
        migrations.AddIndex(
            model_name="staffsecurityaudit",
            index=models.Index(fields=["staff_user", "created_at"], name="staff_sec_user_time_idx"),
        ),
        migrations.AddIndex(
            model_name="staffpasswordresetchallenge",
            index=models.Index(fields=["email_hash_hmac", "created_at"], name="staff_reset_email_time_idx"),
        ),
        migrations.AddIndex(
            model_name="staffpasswordresetchallenge",
            index=models.Index(fields=["status", "expires_at"], name="staff_reset_status_exp_idx"),
        ),
    ]
