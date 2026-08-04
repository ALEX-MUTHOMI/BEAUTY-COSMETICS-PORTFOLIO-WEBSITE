import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0020_service_day_rule_phase_3e"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrivacyRightsRequest",
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
                ("ticket_id", models.CharField(db_index=True, max_length=32, unique=True)),
                (
                    "request_type",
                    models.CharField(
                        choices=[
                            ("access", "Access"),
                            ("erasure", "Erasure"),
                            ("rectification", "Rectification"),
                            ("objection", "Objection"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("accepted", "Accepted"),
                            ("in_progress", "In Progress"),
                            ("fulfilled", "Fulfilled"),
                            ("rejected", "Rejected"),
                        ],
                        default="accepted",
                        max_length=32,
                    ),
                ),
                ("email_hash_hmac", models.CharField(db_index=True, max_length=128)),
                ("phone_hash_hmac", models.CharField(blank=True, db_index=True, max_length=128)),
                ("details_hash_hmac", models.CharField(blank=True, max_length=128)),
                ("correlation_id", models.CharField(blank=True, max_length=128)),
                ("ip_hash_hmac", models.CharField(blank=True, max_length=128)),
                ("user_agent_hash_hmac", models.CharField(blank=True, max_length=128)),
            ],
            options={
                "db_table": "booking_privacy_rights_requests",
                "indexes": [
                    models.Index(fields=["status", "created_at"], name="privacy_rights_status_time_idx"),
                    models.Index(fields=["request_type", "created_at"], name="privacy_rights_type_time_idx"),
                ],
            },
        ),
    ]
