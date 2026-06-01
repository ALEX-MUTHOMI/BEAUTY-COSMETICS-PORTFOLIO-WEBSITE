import secrets
import uuid
from datetime import timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Func, Q, Value
from django.utils import timezone

from core.models import AuditMixin


class TstzRange(Func):
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


def _require_aware_utc(value, field_name):
    if value is None:
        return
    if timezone.is_naive(value):
        raise ValidationError({field_name: "Datetime must be timezone-aware."})


BOOKING_BLOCKING_STATUSES = [
    "held",
    "payment_pending",
    "confirmed",
    "reschedule_held",
    "checked_in",
    "late",
    "in_progress",
]
# Only these lifecycle states reserve resource capacity in PostgreSQL. Terminal
# and non-reserving states stay outside the overlap constraint.


class Service(AuditMixin):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=140, unique=True)
    category = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    buffer_before_minutes = models.PositiveSmallIntegerField(default=0)
    buffer_after_minutes = models.PositiveSmallIntegerField(default=0)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    urgent_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sunday_surcharge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    urgent_allowed = models.BooleanField(default=False)
    sunday_urgent_allowed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_services"
        indexes = [
            models.Index(fields=["slug"], name="booking_service_slug_idx"),
            models.Index(fields=["is_active"], name="booking_service_active_idx"),
        ]

    def clean(self):
        if not 30 <= self.duration_minutes <= 180:
            raise ValidationError({"duration_minutes": "Duration must be between 30 and 180 minutes."})
        for field in ("base_price", "urgent_fee", "sunday_surcharge"):
            if getattr(self, field) < Decimal("0.00"):
                raise ValidationError({field: "Price values cannot be negative."})


class BookableResource(AuditMixin):
    class Type(models.TextChoices):
        BEAUTICIAN = "beautician", "Beautician"
        ROOM = "room", "Room"
        CHAIR = "chair", "Chair"
        EQUIPMENT = "equipment", "Equipment"

    name = models.CharField(max_length=128)
    resource_type = models.CharField(max_length=32, choices=Type.choices, default=Type.BEAUTICIAN)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_resources"
        indexes = [models.Index(fields=["resource_type", "is_active"], name="booking_resource_type_idx")]


class BusinessHours(AuditMixin):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    opens_at = models.TimeField(null=True, blank=True)
    closes_at = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    resource = models.ForeignKey(
        BookableResource,
        on_delete=models.CASCADE,
        related_name="business_hours",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "booking_business_hours"
        constraints = [
            models.UniqueConstraint(fields=["resource", "weekday"], name="uniq_business_hours_resource_weekday"),
        ]

    def clean(self):
        if not self.is_closed and self.opens_at and self.closes_at and self.opens_at >= self.closes_at:
            raise ValidationError("Opening time must be before closing time.")

    @classmethod
    def create_default_week(cls, resource=None):
        from datetime import time

        rows = []
        for weekday in cls.Weekday.values:
            is_sunday = weekday == cls.Weekday.SUNDAY
            rows.append(
                cls.objects.create(
                    resource=resource,
                    weekday=weekday,
                    opens_at=None if is_sunday else time(7, 0),
                    closes_at=None if is_sunday else time(19, 0),
                    is_closed=is_sunday,
                )
            )
        return rows


class BlackoutPeriod(AuditMixin):
    resource = models.ForeignKey(
        BookableResource,
        on_delete=models.CASCADE,
        related_name="blackouts",
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    reason = models.CharField(max_length=255)
    full_day = models.BooleanField(default=False)

    class Meta:
        db_table = "booking_blackout_periods"

    def clean(self):
        _require_aware_utc(self.starts_at, "starts_at")
        _require_aware_utc(self.ends_at, "ends_at")
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValidationError("Blackout starts_at must be before ends_at.")


class BookingPolicy(AuditMixin):
    slot_interval_minutes = models.PositiveSmallIntegerField(default=30)
    default_hold_minutes = models.PositiveSmallIntegerField(default=10)
    abuse_hold_minutes = models.PositiveSmallIntegerField(default=3)
    late_grace_minutes = models.PositiveSmallIntegerField(default=30)
    max_daily_bookings = models.PositiveSmallIntegerField(default=8)
    max_daily_urgent_bookings = models.PositiveSmallIntegerField(default=2)
    max_sunday_urgent_bookings = models.PositiveSmallIntegerField(default=1)
    max_reschedules_per_booking = models.PositiveSmallIntegerField(default=2)
    reschedule_cutoff_hours = models.PositiveSmallIntegerField(default=24)
    require_turnstile_under_abuse = models.BooleanField(default=True)
    require_otp_before_hold_under_abuse = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_policies"


class CustomerProfile(AuditMixin):
    # Operational PII is split three ways: encrypted for reminders, HMAC for
    # lookup, and redacted for logs/dashboard. Raw values must never be stored.
    full_name_encrypted = models.TextField(blank=True)
    full_name_display = models.CharField(max_length=80)
    email_encrypted = models.TextField(blank=True)
    email_hash_hmac = models.CharField(max_length=128, db_index=True)
    email_redacted = models.CharField(max_length=128)
    phone_encrypted = models.TextField(blank=True)
    phone_hash_hmac = models.CharField(max_length=128, db_index=True)
    phone_redacted = models.CharField(max_length=32)
    reminder_consent = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    erased_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_customer_profiles"
        indexes = [
            models.Index(fields=["phone_hash_hmac"], name="booking_customer_phone_hash_idx"),
            models.Index(fields=["email_hash_hmac"], name="booking_customer_email_hash_idx"),
        ]

    @classmethod
    def create_from_plaintext(cls, full_name, email, phone, reminder_consent=False, marketing_consent=False):
        from bookings.privacy import (
            encrypt_value,
            hmac_email_hash,
            hmac_phone_hash,
            normalize_email,
            normalize_phone,
            redact_email,
            redact_phone,
            safe_display_name,
        )

        normalized_email = normalize_email(email)
        normalized_phone = normalize_phone(phone)
        return cls.objects.create(
            full_name_encrypted=encrypt_value(full_name),
            full_name_display=safe_display_name(full_name),
            email_encrypted=encrypt_value(normalized_email),
            email_hash_hmac=hmac_email_hash(normalized_email),
            email_redacted=redact_email(normalized_email),
            phone_encrypted=encrypt_value(normalized_phone),
            phone_hash_hmac=hmac_phone_hash(normalized_phone),
            phone_redacted=redact_phone(normalized_phone),
            reminder_consent=reminder_consent,
            marketing_consent=marketing_consent,
        )

    def erase(self):
        self.full_name_encrypted = ""
        self.email_encrypted = ""
        self.phone_encrypted = ""
        self.full_name_display = "Erased customer"
        self.email_redacted = "erased"
        self.phone_redacted = "erased"
        self.erased_at = timezone.now()
        self.save(
            update_fields=[
                "full_name_encrypted",
                "email_encrypted",
                "phone_encrypted",
                "full_name_display",
                "email_redacted",
                "phone_redacted",
                "erased_at",
                "updated_at",
            ]
        )


class Booking(AuditMixin):
    class Status(models.TextChoices):
        # Status changes must go through bookings.services.state_machine. The
        # overlap constraint only blocks capacity for BOOKING_BLOCKING_STATUSES.
        REQUESTED = "requested", "Requested"
        HELD = "held", "Held"
        PAYMENT_PENDING = "payment_pending", "Payment Pending"
        CONFIRMED = "confirmed", "Confirmed"
        RESCHEDULE_REQUESTED = "reschedule_requested", "Reschedule Requested"
        RESCHEDULE_HELD = "reschedule_held", "Reschedule Held"
        RESCHEDULED = "rescheduled", "Rescheduled"
        CHECKED_IN = "checked_in", "Checked In"
        LATE = "late", "Late"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"
        PAYMENT_FAILED = "payment_failed", "Payment Failed"
        CANCELLED_BY_CLIENT = "cancelled_by_client", "Cancelled by Client"
        CANCELLED_BY_BUSINESS = "cancelled_by_business", "Cancelled by Business"
        NO_SHOW = "no_show", "No Show"

    class BookingType(models.TextChoices):
        NORMAL = "normal", "Normal"
        URGENT = "urgent", "Urgent"
        SUNDAY_URGENT = "sunday_urgent", "Sunday Urgent"

    # public_id is the only customer-facing identifier; internal UUIDs must not
    # be exposed in public lookup/status flows.
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_profile = models.ForeignKey(CustomerProfile, on_delete=models.PROTECT, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    resource = models.ForeignKey(BookableResource, on_delete=models.PROTECT, related_name="bookings")
    # Persist UTC-aware datetimes only. Africa/Nairobi conversion belongs in
    # policy/presentation code before save.
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    booking_type = models.CharField(max_length=32, choices=BookingType.choices, default=BookingType.NORMAL)
    urgency_reason = models.CharField(max_length=255, blank=True)
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    checkout_session_id = models.CharField(max_length=128, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    no_show_at = models.DateTimeField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    reschedule_count = models.PositiveSmallIntegerField(default=0)
    no_refund_policy_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
    terms_version = models.CharField(max_length=32, default="v1")
    privacy_version = models.CharField(max_length=32, default="v1")

    class Meta:
        db_table = "bookings"
        constraints = [
            # Range semantics are [starts_at, ends_at): adjacent bookings are
            # valid, but overlapping blocking-state bookings for one resource
            # are rejected by PostgreSQL under concurrency.
            ExclusionConstraint(
                name="exclude_booking_resource_overlap",
                expressions=[
                    ("resource", RangeOperators.EQUAL),
                    (
                        TstzRange("starts_at", "ends_at", Value("[)")),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(status__in=BOOKING_BLOCKING_STATUSES),
            ),
        ]
        indexes = [
            models.Index(fields=["public_id"], name="bookings_public_id_idx"),
            models.Index(fields=["resource", "starts_at"], name="bookings_resource_start_idx"),
            models.Index(fields=["status"], name="bookings_status_idx"),
        ]

    def clean(self):
        for field in (
            "starts_at",
            "ends_at",
            "hold_expires_at",
            "confirmed_at",
            "checked_in_at",
            "completed_at",
            "no_show_at",
            "no_refund_policy_accepted_at",
            "privacy_policy_accepted_at",
        ):
            _require_aware_utc(getattr(self, field), field)
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValidationError("Booking starts_at must be before ends_at.")

    def save(self, *args, **kwargs):
        for field in (
            "starts_at",
            "ends_at",
            "hold_expires_at",
            "confirmed_at",
            "checked_in_at",
            "completed_at",
            "no_show_at",
            "no_refund_policy_accepted_at",
            "privacy_policy_accepted_at",
        ):
            value = getattr(self, field)
            if value is not None and timezone.is_aware(value):
                setattr(self, field, value.astimezone(dt_timezone.utc))
        self.full_clean(validate_constraints=False)
        super().save(*args, **kwargs)


class BookingPriceSnapshot(AuditMixin):
    # Booking snapshots are operational display history only. Billing remains
    # the financial source of truth.
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name="price_snapshot")
    base_service_price = models.DecimalField(max_digits=12, decimal_places=2)
    urgent_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sunday_surcharge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")

    class Meta:
        db_table = "booking_price_snapshots"


class BookingFinancialHistory(AuditMixin):
    # This model stores booking-visible financial milestones, not ledger truth.
    # Corrections/refunds/reversals belong in billing/.
    class EventType(models.TextChoices):
        CHECKOUT_LINKED = "checkout_linked", "Checkout Linked"
        PAYMENT_CONFIRMED = "payment_confirmed", "Payment Confirmed"
        PAYMENT_FAILED = "payment_failed", "Payment Failed"

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="financial_history")
    checkout_session_id = models.CharField(max_length=128, blank=True)
    billing_ledger_id = models.CharField(max_length=128, blank=True)
    event_type = models.CharField(max_length=64, choices=EventType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    provider_reference_hash = models.CharField(max_length=128, blank=True)
    no_refund_policy_version = models.CharField(max_length=32)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "booking_financial_history"


class BookingReceipt(AuditMixin):
    class PdfStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATED = "generated", "Generated"
        FAILED = "failed", "Failed"

    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name="receipt")
    receipt_number = models.CharField(max_length=48, unique=True)
    checkout_session_id = models.CharField(max_length=128, unique=True)
    billing_ledger_id = models.CharField(max_length=128, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    payment_method = models.CharField(max_length=32, default="M-Pesa")
    payment_status = models.CharField(max_length=32, default="paid")
    booking_status = models.CharField(max_length=32, default=Booking.Status.CONFIRMED)
    issued_at = models.DateTimeField(default=timezone.now)
    receipt_snapshot_json_redacted = models.JSONField(default=dict, blank=True)
    pdf_status = models.CharField(max_length=16, choices=PdfStatus.choices, default=PdfStatus.PENDING)
    pdf_storage_key = models.CharField(max_length=255, null=True, blank=True)
    download_token_hash = models.CharField(max_length=128, null=True, blank=True)
    download_token_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_receipts"
        indexes = [
            models.Index(fields=["receipt_number"], name="booking_receipt_number_idx"),
            models.Index(fields=["download_token_hash"], name="booking_receipt_token_idx"),
        ]

    def issue_download_token(self, *, ttl_minutes=30):
        from billing.redaction import hash_sensitive_value

        token = secrets.token_urlsafe(32)
        self.download_token_hash = hash_sensitive_value(token)
        self.download_token_expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
        self.save(update_fields=["download_token_hash", "download_token_expires_at", "updated_at"])
        return token


class BookingNotification(AuditMixin):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="notifications")
    receipt = models.ForeignKey(
        BookingReceipt,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=64)
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.EMAIL)
    recipient_email_hash = models.CharField(max_length=128, blank=True)
    recipient_email_redacted = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    scheduled_for = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error_redacted = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_notifications"
        constraints = [
            models.UniqueConstraint(
                fields=["booking", "notification_type", "channel"],
                name="uniq_booking_notification_type_channel",
            ),
        ]
        indexes = [models.Index(fields=["status", "scheduled_for"], name="booking_notif_due_idx")]

    def clean(self):
        _require_aware_utc(self.scheduled_for, "scheduled_for")
        _require_aware_utc(self.sent_at, "sent_at")


class BookingRescheduleRequest(AuditMixin):
    # The old slot must not be released until a replacement slot is safely held.
    # Additional-fee reschedules later go through checkout, not ledger mutation.
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        HELD = "held", "Held"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="reschedule_requests")
    requested_starts_at = models.DateTimeField()
    requested_ends_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    expires_at = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    additional_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    new_checkout_session_id = models.CharField(max_length=128, blank=True)
    original_billing_ledger_id = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "booking_reschedule_requests"

    def clean(self):
        _require_aware_utc(self.requested_starts_at, "requested_starts_at")
        _require_aware_utc(self.requested_ends_at, "requested_ends_at")
        _require_aware_utc(self.expires_at, "expires_at")
        if self.requested_starts_at and self.requested_ends_at and self.requested_starts_at >= self.requested_ends_at:
            raise ValidationError("Requested starts_at must be before requested ends_at.")


class BookingReminder(AuditMixin):
    # Durable transactional outbox. Celery/Redis delivery is a consumer of this
    # table, not the source of truth for reminder intent.
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        SKIPPED = "skipped", "Skipped"

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="reminders")
    channel = models.CharField(max_length=16, choices=Channel.choices)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    failure_reason_redacted = models.CharField(max_length=255, blank=True)
    provider_message_id_hash = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "booking_reminders"
        indexes = [models.Index(fields=["status", "scheduled_for"], name="booking_reminder_due_idx")]

    def clean(self):
        _require_aware_utc(self.scheduled_for, "scheduled_for")
        _require_aware_utc(self.sent_at, "sent_at")


class BookingAuditEvent(AuditMixin):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="audit_events")
    old_status = models.CharField(max_length=32, blank=True)
    new_status = models.CharField(max_length=32)
    reason = models.CharField(max_length=255, blank=True)
    actor_type = models.CharField(max_length=32)
    actor_id = models.CharField(max_length=128, null=True, blank=True)
    request_id = models.CharField(max_length=128, null=True, blank=True)
    metadata_redacted = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "booking_audit_events"


class StaffActionAuditEvent(AuditMixin):
    # Contact reveal and staff overrides are high-risk privacy events. Store
    # redacted metadata only and require RBAC in service-layer callers.
    class Action(models.TextChoices):
        CONTACT_REVEAL = "contact_reveal", "Contact Reveal"
        STATUS_OVERRIDE = "status_override", "Status Override"

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="booking_staff_audit_events",
    )
    action = models.CharField(max_length=64, choices=Action.choices)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, null=True, blank=True)
    reason = models.CharField(max_length=255)
    metadata_redacted = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "booking_staff_action_audit_events"
