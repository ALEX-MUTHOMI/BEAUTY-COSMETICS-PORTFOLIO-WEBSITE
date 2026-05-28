# Generated manually for Phase 2B financial ledger architecture.

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
            name="LedgerTransaction",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "mpesa_receipt_number",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                ("checkout_request_id", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("credited_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ledger_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "billing_ledger_transactions",
            },
        ),
        migrations.AddIndex(
            model_name="ledgertransaction",
            index=models.Index(
                fields=["checkout_request_id"], name="billing_led_checkou_fa4706_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="ledgertransaction",
            index=models.Index(fields=["status"], name="billing_led_status_2ca63f_idx"),
        ),
        migrations.AddConstraint(
            model_name="ledgertransaction",
            constraint=models.UniqueConstraint(
                fields=("checkout_request_id",), name="uniq_ledger_checkout_request_id"
            ),
        ),
    ]
