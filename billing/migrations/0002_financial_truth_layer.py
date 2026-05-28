# Generated manually for Phase 2C-A billing truth layer.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="ledgertransaction",
            name="currency",
            field=models.CharField(default="KES", max_length=3),
        ),
        migrations.AddField(
            model_name="ledgertransaction",
            name="direction",
            field=models.CharField(
                choices=[("debit", "Debit"), ("credit", "Credit")],
                default="credit",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="ledgertransaction",
            name="provider",
            field=models.CharField(
                choices=[("mpesa", "M-Pesa"), ("internal", "Internal")],
                default="mpesa",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="ledgertransaction",
            name="provider_reference_hash",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="ledgertransaction",
            name="provider_receipt_hash",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="ledgertransaction",
            name="external_correlation_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="ledgertransaction",
            name="checkout_request_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="ledgertransaction",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("success", "Success"),
                    ("failed", "Failed"),
                    ("reversed", "Reversed"),
                    ("refunded", "Refunded"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
        migrations.CreateModel(
            name="FinancialAuditEvent",
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
                ("event_type", models.CharField(max_length=64)),
                ("source", models.CharField(default="system", max_length=64)),
                ("redacted_payload", models.JSONField(blank=True, default=dict)),
                ("payload_hash", models.CharField(max_length=128)),
                (
                    "correlation_id",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                (
                    "ledger_transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="audit_events",
                        to="billing.ledgertransaction",
                    ),
                ),
            ],
            options={"db_table": "billing_financial_audit_events"},
        ),
        migrations.CreateModel(
            name="SettlementRecord",
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
                    "recipient_reference",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                (
                    "settlement_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("ready", "Ready"),
                            ("settled", "Settled"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="KES", max_length=3)),
                ("settled_at", models.DateTimeField(blank=True, null=True)),
                (
                    "ledger_transaction",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="settlement_record",
                        to="billing.ledgertransaction",
                    ),
                ),
            ],
            options={"db_table": "billing_settlement_records"},
        ),
        migrations.AddIndex(
            model_name="ledgertransaction",
            index=models.Index(
                fields=["provider_reference_hash"],
                name="billing_led_provide_884b14_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="ledgertransaction",
            index=models.Index(
                fields=["external_correlation_id"],
                name="billing_led_externa_6c94fc_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="financialauditevent",
            index=models.Index(
                fields=["event_type"], name="billing_fin_event_t_79a315_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="financialauditevent",
            index=models.Index(
                fields=["correlation_id"], name="billing_fin_correla_651b38_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="settlementrecord",
            index=models.Index(
                fields=["settlement_status"], name="billing_set_settlem_ed3beb_idx"
            ),
        ),
    ]
