# Generated for Phase 2C-B1 booking domain foundation.

import uuid
from decimal import Decimal

import django.db.models.deletion
from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations, models
from django.db.models import Func, Q, Value
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0003_booking_duration_minutes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        BtreeGistExtension(),
        migrations.DeleteModel(name="Booking"),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=128)),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("category", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True)),
                ("duration_minutes", models.PositiveSmallIntegerField(default=60)),
                ("buffer_before_minutes", models.PositiveSmallIntegerField(default=0)),
                ("buffer_after_minutes", models.PositiveSmallIntegerField(default=0)),
                ("base_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("urgent_fee", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("sunday_surcharge", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("urgent_allowed", models.BooleanField(default=False)),
                ("sunday_urgent_allowed", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "booking_services"},
        ),
        migrations.CreateModel(
            name="BookableResource",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=128)),
                (
                    "resource_type",
                    models.CharField(
                        choices=[
                            ("beautician", "Beautician"),
                            ("room", "Room"),
                            ("chair", "Chair"),
                            ("equipment", "Equipment"),
                        ],
                        default="beautician",
                        max_length=32,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "booking_resources"},
        ),
        migrations.CreateModel(
            name="BookingPolicy",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("slot_interval_minutes", models.PositiveSmallIntegerField(default=30)),
                ("default_hold_minutes", models.PositiveSmallIntegerField(default=10)),
                ("abuse_hold_minutes", models.PositiveSmallIntegerField(default=3)),
                ("late_grace_minutes", models.PositiveSmallIntegerField(default=30)),
                ("max_daily_bookings", models.PositiveSmallIntegerField(default=8)),
                ("max_daily_urgent_bookings", models.PositiveSmallIntegerField(default=2)),
                ("max_sunday_urgent_bookings", models.PositiveSmallIntegerField(default=1)),
                ("max_reschedules_per_booking", models.PositiveSmallIntegerField(default=2)),
                ("reschedule_cutoff_hours", models.PositiveSmallIntegerField(default=24)),
                ("require_turnstile_under_abuse", models.BooleanField(default=True)),
                ("require_otp_before_hold_under_abuse", models.BooleanField(default=True)),
            ],
            options={"db_table": "booking_policies"},
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("full_name_encrypted", models.TextField(blank=True)),
                ("full_name_display", models.CharField(max_length=80)),
                ("email_encrypted", models.TextField(blank=True)),
                ("email_hash_hmac", models.CharField(db_index=True, max_length=128)),
                ("email_redacted", models.CharField(max_length=128)),
                ("phone_encrypted", models.TextField(blank=True)),
                ("phone_hash_hmac", models.CharField(db_index=True, max_length=128)),
                ("phone_redacted", models.CharField(max_length=32)),
                ("reminder_consent", models.BooleanField(default=False)),
                ("marketing_consent", models.BooleanField(default=False)),
                ("erased_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"db_table": "booking_customer_profiles"},
        ),
        migrations.CreateModel(
            name="BusinessHours",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "weekday",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ]
                    ),
                ),
                ("opens_at", models.TimeField(blank=True, null=True)),
                ("closes_at", models.TimeField(blank=True, null=True)),
                ("is_closed", models.BooleanField(default=False)),
                (
                    "resource",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="business_hours",
                        to="bookings.bookableresource",
                    ),
                ),
            ],
            options={"db_table": "booking_business_hours"},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("held", "Held"),
                            ("payment_pending", "Payment Pending"),
                            ("confirmed", "Confirmed"),
                            ("reschedule_requested", "Reschedule Requested"),
                            ("reschedule_held", "Reschedule Held"),
                            ("rescheduled", "Rescheduled"),
                            ("checked_in", "Checked In"),
                            ("late", "Late"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("expired", "Expired"),
                            ("payment_failed", "Payment Failed"),
                            ("cancelled_by_client", "Cancelled by Client"),
                            ("cancelled_by_business", "Cancelled by Business"),
                            ("no_show", "No Show"),
                        ],
                        default="requested",
                        max_length=32,
                    ),
                ),
                (
                    "booking_type",
                    models.CharField(
                        choices=[
                            ("normal", "Normal"),
                            ("urgent", "Urgent"),
                            ("sunday_urgent", "Sunday Urgent"),
                        ],
                        default="normal",
                        max_length=32,
                    ),
                ),
                ("urgency_reason", models.CharField(blank=True, max_length=255)),
                ("hold_expires_at", models.DateTimeField(blank=True, null=True)),
                ("checkout_session_id", models.CharField(blank=True, max_length=128)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("checked_in_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("no_show_at", models.DateTimeField(blank=True, null=True)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("reschedule_count", models.PositiveSmallIntegerField(default=0)),
                ("no_refund_policy_accepted_at", models.DateTimeField(blank=True, null=True)),
                ("privacy_policy_accepted_at", models.DateTimeField(blank=True, null=True)),
                ("terms_version", models.CharField(default="v1", max_length=32)),
                ("privacy_version", models.CharField(default="v1", max_length=32)),
                (
                    "customer_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to="bookings.customerprofile",
                    ),
                ),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to="bookings.bookableresource",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to="bookings.service",
                    ),
                ),
            ],
            options={"db_table": "bookings"},
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=ExclusionConstraint(
                name="exclude_booking_resource_overlap",
                expressions=[
                    ("resource", RangeOperators.EQUAL),
                    (
                        Func(
                            "starts_at",
                            "ends_at",
                            Value("[)"),
                            function="TSTZRANGE",
                            output_field=DateTimeRangeField(),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(
                    (
                        "status__in",
                        [
                            "held",
                            "payment_pending",
                            "confirmed",
                            "reschedule_held",
                            "checked_in",
                            "late",
                            "in_progress",
                        ],
                    )
                ),
            ),
        ),
        migrations.CreateModel(
            name="BlackoutPeriod",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("reason", models.CharField(max_length=255)),
                ("full_day", models.BooleanField(default=False)),
                (
                    "resource",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blackouts",
                        to="bookings.bookableresource",
                    ),
                ),
            ],
            options={"db_table": "booking_blackout_periods"},
        ),
        migrations.CreateModel(
            name="BookingPriceSnapshot",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("base_service_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("urgent_fee", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("sunday_surcharge", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="KES", max_length=3)),
                (
                    "booking",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="price_snapshot",
                        to="bookings.booking",
                    ),
                ),
            ],
            options={"db_table": "booking_price_snapshots"},
        ),
        migrations.CreateModel(
            name="BookingFinancialHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("checkout_session_id", models.CharField(blank=True, max_length=128)),
                ("billing_ledger_id", models.CharField(blank=True, max_length=128)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("checkout_linked", "Checkout Linked"),
                            ("payment_confirmed", "Payment Confirmed"),
                            ("payment_failed", "Payment Failed"),
                        ],
                        max_length=64,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="KES", max_length=3)),
                ("provider_reference_hash", models.CharField(blank=True, max_length=128)),
                ("no_refund_policy_version", models.CharField(max_length=32)),
                ("occurred_at", models.DateTimeField(default=timezone.now)),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="financial_history",
                        to="bookings.booking",
                    ),
                ),
            ],
            options={"db_table": "booking_financial_history"},
        ),
        migrations.CreateModel(
            name="BookingRescheduleRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("requested_starts_at", models.DateTimeField()),
                ("requested_ends_at", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("held", "Held"),
                            ("accepted", "Accepted"),
                            ("expired", "Expired"),
                            ("rejected", "Rejected"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="requested",
                        max_length=32,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("additional_fee_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("new_checkout_session_id", models.CharField(blank=True, max_length=128)),
                ("original_billing_ledger_id", models.CharField(blank=True, max_length=128)),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reschedule_requests",
                        to="bookings.booking",
                    ),
                ),
            ],
            options={"db_table": "booking_reschedule_requests"},
        ),
        migrations.CreateModel(
            name="BookingReminder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "channel",
                    models.CharField(choices=[("email", "Email"), ("sms", "SMS"), ("whatsapp", "WhatsApp")], max_length=16),
                ),
                ("scheduled_for", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("sent", "Sent"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                            ("skipped", "Skipped"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("failure_reason_redacted", models.CharField(blank=True, max_length=255)),
                ("provider_message_id_hash", models.CharField(blank=True, max_length=128)),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reminders",
                        to="bookings.booking",
                    ),
                ),
            ],
            options={"db_table": "booking_reminders"},
        ),
        migrations.CreateModel(
            name="BookingAuditEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("old_status", models.CharField(blank=True, max_length=32)),
                ("new_status", models.CharField(max_length=32)),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("actor_type", models.CharField(max_length=32)),
                ("actor_id", models.CharField(blank=True, max_length=128, null=True)),
                ("request_id", models.CharField(blank=True, max_length=128, null=True)),
                ("metadata_redacted", models.JSONField(blank=True, default=dict)),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="audit_events",
                        to="bookings.booking",
                    ),
                ),
            ],
            options={"db_table": "booking_audit_events"},
        ),
        migrations.CreateModel(
            name="StaffActionAuditEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "action",
                    models.CharField(
                        choices=[("contact_reveal", "Contact Reveal"), ("status_override", "Status Override")],
                        max_length=64,
                    ),
                ),
                ("reason", models.CharField(max_length=255)),
                ("metadata_redacted", models.JSONField(blank=True, default=dict)),
                (
                    "booking",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="bookings.booking",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="booking_staff_audit_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "booking_staff_action_audit_events"},
        ),
        migrations.AddConstraint(
            model_name="businesshours",
            constraint=models.UniqueConstraint(fields=("resource", "weekday"), name="uniq_business_hours_resource_weekday"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["slug"], name="booking_service_slug_idx"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["is_active"], name="booking_service_active_idx"),
        ),
        migrations.AddIndex(
            model_name="bookableresource",
            index=models.Index(fields=["resource_type", "is_active"], name="booking_resource_type_idx"),
        ),
        migrations.AddIndex(
            model_name="customerprofile",
            index=models.Index(fields=["phone_hash_hmac"], name="booking_customer_phone_hash_idx"),
        ),
        migrations.AddIndex(
            model_name="customerprofile",
            index=models.Index(fields=["email_hash_hmac"], name="booking_customer_email_hash_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["public_id"], name="bookings_public_id_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["resource", "starts_at"], name="bookings_resource_start_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["status"], name="bookings_status_idx"),
        ),
        migrations.AddIndex(
            model_name="bookingreminder",
            index=models.Index(fields=["status", "scheduled_for"], name="booking_reminder_due_idx"),
        ),
    ]
