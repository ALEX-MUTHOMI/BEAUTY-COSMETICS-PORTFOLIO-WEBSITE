# Generated manually for Phase 2C-A checkout orchestration domain.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CheckoutSession",
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
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the database record was last saved.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                (
                    "amount_snapshot",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                ("currency", models.CharField(default="KES", max_length=3)),
                ("description_snapshot", models.CharField(max_length=255)),
                ("purchasable_type", models.CharField(max_length=64)),
                ("purchasable_id", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("payment_pending", "Payment Pending"),
                            ("stk_sent", "STK Sent"),
                            ("paid", "Paid"),
                            ("failed", "Failed"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="created",
                        max_length=32,
                    ),
                ),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("expires_at", models.DateTimeField()),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="checkout_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "checkout_sessions"},
        ),
        migrations.CreateModel(
            name="CheckoutAttempt",
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
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the database record was last saved.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                (
                    "provider",
                    models.CharField(choices=[("mpesa", "M-Pesa")], default="mpesa", max_length=32),
                ),
                ("phone_number_hash", models.CharField(max_length=128)),
                ("redacted_phone", models.CharField(max_length=32)),
                ("provider_request_id", models.CharField(max_length=128, unique=True)),
                ("merchant_request_id", models.CharField(max_length=128, unique=True)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("initiated", "Initiated"),
                            ("sent", "Sent"),
                            ("callback_received", "Callback Received"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                            ("timeout", "Timeout"),
                        ],
                        default="initiated",
                        max_length=32,
                    ),
                ),
                ("raw_request_hash", models.CharField(max_length=128)),
                (
                    "redacted_request_payload",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "checkout_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="attempts",
                        to="checkout.checkoutsession",
                    ),
                ),
            ],
            options={"db_table": "checkout_attempts"},
        ),
        migrations.CreateModel(
            name="MpesaWebhookInbox",
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
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the database record was last saved.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                ("provider", models.CharField(default="mpesa", max_length=32)),
                ("event_hash", models.CharField(max_length=128, unique=True)),
                (
                    "checkout_request_id_hash",
                    models.CharField(blank=True, max_length=128),
                ),
                ("redacted_payload", models.JSONField(blank=True, default=dict)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "processing_status",
                    models.CharField(
                        choices=[
                            ("received", "Received"),
                            ("processed", "Processed"),
                            ("duplicate", "Duplicate"),
                            ("rejected", "Rejected"),
                            ("failed", "Failed"),
                        ],
                        default="received",
                        max_length=16,
                    ),
                ),
                (
                    "correlation_id",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
            ],
            options={"db_table": "checkout_mpesa_webhook_inbox"},
        ),
        migrations.AddIndex(
            model_name="checkoutsession",
            index=models.Index(fields=["customer", "status"], name="checkout_se_customer_b2a808_idx"),
        ),
        migrations.AddIndex(
            model_name="checkoutsession",
            index=models.Index(fields=["expires_at"], name="checkout_se_expires_709e52_idx"),
        ),
        migrations.AddIndex(
            model_name="checkoutattempt",
            index=models.Index(fields=["provider_request_id"], name="checkout_at_provide_5b9f73_idx"),
        ),
        migrations.AddIndex(
            model_name="checkoutattempt",
            index=models.Index(fields=["status"], name="checkout_at_status_7b4fc8_idx"),
        ),
        migrations.AddIndex(
            model_name="mpesawebhookinbox",
            index=models.Index(
                fields=["checkout_request_id_hash"],
                name="checkout_mp_checkou_6bf486_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="mpesawebhookinbox",
            index=models.Index(fields=["processing_status"], name="checkout_mp_process_f56310_idx"),
        ),
    ]
