# Generated manually for Phase 2B booking and billing bridge architecture.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("billing", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
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
                    "service_name",
                    models.CharField(default="Beauty consultation", max_length=128),
                ),
                ("service_date", models.DateField()),
                ("time_slot", models.CharField(max_length=16)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_payment", "Pending Payment"),
                            ("confirmed", "Confirmed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending_payment",
                        max_length=32,
                    ),
                ),
                (
                    "ledger_transaction",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="booking",
                        to="billing.ledgertransaction",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "bookings",
            },
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["service_date", "time_slot"], name="bookings_service_f1f4bf_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["status"], name="bookings_status_595c9d_idx"),
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=models.UniqueConstraint(
                fields=("service_date", "time_slot"),
                name="uniq_booking_service_date_time_slot",
            ),
        ),
    ]
