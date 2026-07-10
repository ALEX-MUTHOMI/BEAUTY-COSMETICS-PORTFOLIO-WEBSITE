import hashlib
import secrets
import uuid
from datetime import timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

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
    category_ref = models.ForeignKey(
        "ServiceCategory",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="services",
    )
    subcategory = models.ForeignKey(
        "ServiceSubcategory",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="services",
    )
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    buffer_before_minutes = models.PositiveSmallIntegerField(default=0)
    buffer_after_minutes = models.PositiveSmallIntegerField(default=0)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    urgent_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sunday_surcharge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    urgent_allowed = models.BooleanField(default=False)
    sunday_urgent_allowed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "booking_services"
        indexes = [
            models.Index(fields=["slug"], name="booking_service_slug_idx"),
            models.Index(fields=["is_active"], name="booking_service_active_idx"),
            models.Index(fields=["category_ref", "subcategory", "is_active"], name="booking_service_catalog_idx"),
        ]

    def clean(self):
        if not 30 <= self.duration_minutes <= 180:
            raise ValidationError({"duration_minutes": "Duration must be between 30 and 180 minutes."})
        for field in ("base_price", "urgent_fee", "sunday_surcharge"):
            if getattr(self, field) < Decimal("0.00"):
                raise ValidationError({field: "Price values cannot be negative."})


class ServiceCategory(AuditMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=140, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_service_categories"
        indexes = [
            models.Index(fields=["slug", "is_active"], name="svc_cat_slug_active_idx"),
            models.Index(fields=["sort_order", "is_active"], name="service_category_sort_idx"),
        ]


class ServiceSubcategory(AuditMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="subcategories")
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=140)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_service_subcategories"
        constraints = [
            models.UniqueConstraint(fields=["category", "slug"], name="uniq_service_subcategory_slug"),
        ]
        indexes = [
            models.Index(fields=["category", "slug", "is_active"], name="svc_subcat_slug_act_idx"),
            models.Index(fields=["category", "sort_order", "is_active"], name="service_subcategory_sort_idx"),
        ]


class FullPackage(AuditMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField()
    buffer_after_minutes = models.PositiveSmallIntegerField(default=0)
    price_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    notice_required_hours = models.PositiveSmallIntegerField(default=24)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_full_packages"
        indexes = [
            models.Index(fields=["slug", "is_active"], name="full_package_slug_active_idx"),
            models.Index(fields=["sort_order", "is_active"], name="full_package_sort_idx"),
        ]

    def clean(self):
        if self.duration_minutes <= 0:
            raise ValidationError({"duration_minutes": "Package duration must be positive."})
        if self.price_amount < Decimal("0.00"):
            raise ValidationError({"price_amount": "Package price cannot be negative."})


class BookingDayPolicy(AuditMixin):
    class DayType(models.TextChoices):
        NORMAL = "normal", "Normal"
        FULL_PACKAGE = "full_package", "Full Package"
        CLOSED = "closed", "Closed"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    weekday = models.PositiveSmallIntegerField(unique=True)
    day_type = models.CharField(max_length=32, choices=DayType.choices)
    business_start_time = models.TimeField()
    business_end_time = models.TimeField()
    max_clients = models.PositiveSmallIntegerField()
    full_package_notice_hours = models.PositiveSmallIntegerField(default=24)
    normal_bookings_allowed = models.BooleanField(default=False)
    full_package_allowed = models.BooleanField(default=False)
    manual_release_allowed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_day_policies"
        indexes = [
            models.Index(fields=["weekday", "is_active"], name="booking_day_policy_weekday_idx"),
            models.Index(fields=["day_type", "is_active"], name="booking_day_policy_type_idx"),
        ]

    def clean(self):
        if self.business_start_time >= self.business_end_time:
            raise ValidationError("Business start time must be before end time.")


class ServiceDayRule(AuditMixin):
    """Optional per-catalog-slug weekday override (Phase 3e extension point).

    When no active row exists, CalendarPolicy uses type-level defaults from 3b
    (packages Tue/Wed, singles Mon/Thu/Fri/Sat). Staff or migrations only — never
    writable from public booking APIs.
    """

    class SelectionType(models.TextChoices):
        NORMAL = "normal", "Normal"
        FULL_PACKAGE = "full_package", "Full Package"

    selection_type = models.CharField(max_length=20, choices=SelectionType.choices)
    catalog_slug = models.SlugField(max_length=140)
    weekday = models.PositiveSmallIntegerField()
    offered = models.BooleanField(null=True, blank=True)
    max_clients = models.PositiveSmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "booking_service_day_rules"
        constraints = [
            models.UniqueConstraint(
                fields=["selection_type", "catalog_slug", "weekday"],
                name="uniq_service_day_rule_slug_weekday",
            ),
            models.CheckConstraint(
                condition=models.Q(weekday__gte=0) & models.Q(weekday__lte=6),
                name="service_day_rule_weekday_range",
            ),
        ]
        indexes = [
            models.Index(
                fields=["selection_type", "catalog_slug", "weekday", "is_active"],
                name="service_day_rule_lookup_idx",
            ),
        ]

    def clean(self):
        if self.offered is None and self.max_clients is None:
            raise ValidationError("Service day rule must set offered and/or max_clients.")
        if self.max_clients is not None and self.max_clients < 0:
            raise ValidationError("max_clients cannot be negative.")


class BookingDayState(AuditMixin):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        FULL = "full", "Full"
        CLOSED = "closed", "Closed"
        MANUALLY_RELEASED = "manually_released", "Manually Released"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    local_date = models.DateField(unique=True)
    timezone_name = models.CharField(max_length=64, default="Africa/Nairobi")
    policy_snapshot_type = models.CharField(max_length=32)
    max_clients_snapshot = models.PositiveSmallIntegerField(default=0)
    active_client_count_snapshot = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)

    class Meta:
        db_table = "booking_day_states"
        indexes = [
            models.Index(fields=["local_date"], name="booking_day_state_date_idx"),
            models.Index(fields=["status", "local_date"], name="booking_day_state_status_idx"),
        ]


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


class LegalDocument(AuditMixin):
    class DocumentType(models.TextChoices):
        TERMS = "terms_of_service", "Terms of Service"
        PRIVACY = "privacy_policy", "Privacy Policy"
        BOOKING_POLICY = "booking_policy", "Booking Policy"
        COOKIE_NOTICE = "cookie_notice", "Cookie Notice"
        DATA_RETENTION = "data_retention_policy", "Data Retention Policy"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        BUSINESS_APPROVED = "business_approved", "Business Approved"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    class LegalReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        NOT_REQUIRED = "not_required", "Not Required"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    document_type = models.CharField(max_length=40, choices=DocumentType.choices)
    version = models.CharField(max_length=32)
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, blank=True)
    effective_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    content_markdown = models.TextField()
    content_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    is_active = models.BooleanField(default=True)
    requires_acceptance = models.BooleanField(default=True)
    replaces_version = models.CharField(max_length=32, blank=True)
    business_approved_at = models.DateTimeField(null=True, blank=True)
    legal_review_status = models.CharField(
        max_length=24,
        choices=LegalReviewStatus.choices,
        default=LegalReviewStatus.PENDING,
    )
    legal_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_legal_documents"
        constraints = [
            models.UniqueConstraint(fields=["document_type", "version"], name="uniq_legal_doc_type_version"),
            models.UniqueConstraint(
                fields=["document_type"],
                condition=Q(status="active"),
                name="uniq_active_legal_doc_type",
            ),
        ]
        indexes = [
            models.Index(fields=["document_type", "is_active"], name="legal_doc_active_type_idx"),
            models.Index(fields=["document_type", "status"], name="legal_doc_status_type_idx"),
            models.Index(fields=["effective_at"], name="legal_doc_effective_idx"),
        ]

    def _computed_hash(self):
        material = "\n".join([self.document_type, self.version, self.title, self.content_markdown])
        return hashlib.sha256(material.encode()).hexdigest()

    def clean(self):
        _require_aware_utc(self.effective_at, "effective_at")
        _require_aware_utc(self.published_at, "published_at")
        _require_aware_utc(self.archived_at, "archived_at")
        _require_aware_utc(self.business_approved_at, "business_approved_at")
        _require_aware_utc(self.legal_reviewed_at, "legal_reviewed_at")
        if not self.content_markdown.strip():
            raise ValidationError({"content_markdown": "Legal document content is required."})

    def save(self, *args, **kwargs):
        for field in (
            "effective_at",
            "published_at",
            "archived_at",
            "business_approved_at",
            "legal_reviewed_at",
        ):
            value = getattr(self, field)
            if value and timezone.is_aware(value):
                setattr(self, field, value.astimezone(dt_timezone.utc))
        if not self.slug:
            self.slug = self.document_type.replace("_", "-")
        if self.status == self.Status.ACTIVE:
            self.is_active = True
            if self.published_at is None:
                self.published_at = timezone.now()
        else:
            self.is_active = False
        if self.status == self.Status.BUSINESS_APPROVED and self.business_approved_at is None:
            self.business_approved_at = timezone.now()
        if self.pk and self.status == self.Status.ACTIVE:
            (
                LegalDocument.objects.filter(document_type=self.document_type, status=self.Status.ACTIVE)
                .exclude(pk=self.pk)
                .update(status=self.Status.ARCHIVED, is_active=False, archived_at=timezone.now())
            )
        elif not self.pk and self.status == self.Status.ACTIVE:
            LegalDocument.objects.filter(document_type=self.document_type, status=self.Status.ACTIVE).update(
                status=self.Status.ARCHIVED,
                is_active=False,
                archived_at=timezone.now(),
            )
        self.content_hash = self._computed_hash()
        self.full_clean(validate_constraints=False)
        super().save(*args, **kwargs)


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
            models.Index(fields=["phone_hash_hmac"], name="bk_cust_phone_hash_idx"),
            models.Index(fields=["email_hash_hmac"], name="bk_cust_email_hash_idx"),
            models.Index(
                fields=["email_hash_hmac", "phone_hash_hmac"],
                name="bk_cust_email_phone_idx",
            ),
            models.Index(fields=["erased_at"], name="booking_customer_erased_idx"),
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
        email_hash = hmac_email_hash(normalized_email)
        phone_hash = hmac_phone_hash(normalized_phone)
        existing = cls.objects.filter(
            email_hash_hmac=email_hash,
            phone_hash_hmac=phone_hash,
            erased_at__isnull=True,
        ).first()
        if existing:
            return existing
        return cls.objects.create(
            full_name_encrypted=encrypt_value(full_name),
            full_name_display=safe_display_name(full_name),
            email_encrypted=encrypt_value(normalized_email),
            email_hash_hmac=email_hash,
            email_redacted=redact_email(normalized_email),
            phone_encrypted=encrypt_value(normalized_phone),
            phone_hash_hmac=phone_hash,
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


class ReturningClientDevice(AuditMixin):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        related_name="returning_devices",
    )
    token_hash_hmac = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=64, blank=True)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)
    token_rotated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_returning_client_devices"
        indexes = [
            models.Index(fields=["token_hash_hmac"], name="return_device_token_hash_idx"),
            models.Index(fields=["customer_profile", "status"], name="return_device_customer_idx"),
            models.Index(fields=["status", "expires_at"], name="return_device_expiry_idx"),
            models.Index(fields=["last_used_at"], name="return_device_used_idx"),
        ]

    def clean(self):
        _require_aware_utc(self.expires_at, "expires_at")
        _require_aware_utc(self.last_used_at, "last_used_at")
        _require_aware_utc(self.revoked_at, "revoked_at")
        _require_aware_utc(self.token_rotated_at, "token_rotated_at")


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
        FULL_PACKAGE = "full_package", "Full Package"

    # public_id is the only customer-facing identifier; internal UUIDs must not
    # be exposed in public lookup/status flows.
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_profile = models.ForeignKey(CustomerProfile, on_delete=models.PROTECT, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True, related_name="bookings")
    resource = models.ForeignKey(BookableResource, on_delete=models.PROTECT, related_name="bookings")
    full_package = models.ForeignKey(
        FullPackage,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bookings",
    )
    # Persist UTC-aware datetimes only. Africa/Nairobi conversion belongs in
    # policy/presentation code before save.
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    local_booking_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    booking_type = models.CharField(max_length=32, choices=BookingType.choices, default=BookingType.NORMAL)
    total_duration_minutes = models.PositiveSmallIntegerField(default=0)
    total_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency_snapshot = models.CharField(max_length=3, default="KES")
    selection_snapshot_json_redacted = models.JSONField(default=dict, blank=True)
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
            models.Index(fields=["resource", "starts_at", "ends_at"], name="bookings_resource_range_idx"),
            models.Index(fields=["status"], name="bookings_status_idx"),
            models.Index(fields=["local_booking_date", "status"], name="bookings_local_date_status_idx"),
            models.Index(
                fields=["booking_type", "local_booking_date", "status"], name="bookings_type_local_status_idx"
            ),
        ]
        permissions = [
            ("view_staff_portal", "Can view staff booking portal schedule"),
            ("view_staff_booking", "Can view staff booking detail"),
            ("view_staff_payment_summary", "Can view staff payment summary"),
            ("view_staff_contact_details", "Can reveal staff contact details"),
            ("manage_staff_booking_notes", "Can manage staff booking notes"),
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
        if self.starts_at:
            self.local_booking_date = self.starts_at.astimezone(ZoneInfo("Africa/Nairobi")).date()
        if not self.total_duration_minutes and self.starts_at and self.ends_at:
            self.total_duration_minutes = max(1, int((self.ends_at - self.starts_at).total_seconds() // 60))
        if self.total_price_snapshot == Decimal("0.00") and self.service_id:
            self.total_price_snapshot = self.service.base_price
            self.currency_snapshot = getattr(self.service, "currency", "KES")
        self.full_clean(validate_constraints=False)
        super().save(*args, **kwargs)


class BookingServiceItem(AuditMixin):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="service_items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="booking_items")
    sequence_order = models.PositiveSmallIntegerField(default=0)
    name_snapshot = models.CharField(max_length=128)
    category_snapshot = models.CharField(max_length=128, blank=True)
    duration_minutes_snapshot = models.PositiveSmallIntegerField()
    price_amount_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    currency_snapshot = models.CharField(max_length=3, default="KES")

    class Meta:
        db_table = "booking_service_items"
        constraints = [
            models.UniqueConstraint(fields=["booking", "service"], name="uniq_booking_service_item"),
        ]
        indexes = [
            models.Index(fields=["booking"], name="booking_item_booking_idx"),
            models.Index(fields=["service"], name="booking_item_service_idx"),
        ]


class BookingPolicyAcceptance(AuditMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="policy_acceptances")
    checkout_session = models.ForeignKey(
        "checkout.CheckoutSession",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="booking_policy_acceptances",
    )
    customer_profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="policy_acceptances",
    )
    terms_version = models.CharField(max_length=32)
    privacy_version = models.CharField(max_length=32)
    booking_policy_version = models.CharField(max_length=32)
    cookie_notice_version = models.CharField(max_length=32, blank=True)
    terms_content_hash = models.CharField(max_length=64, blank=True)
    privacy_content_hash = models.CharField(max_length=64, blank=True)
    booking_policy_content_hash = models.CharField(max_length=64, blank=True)
    cookie_notice_content_hash = models.CharField(max_length=64, blank=True)
    no_refund_ack_hash = models.CharField(max_length=128, blank=True)
    accepted_at = models.DateTimeField(default=timezone.now)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)
    locale = models.CharField(max_length=16, blank=True)
    timezone_name = models.CharField(max_length=64, blank=True)
    country_hint = models.CharField(max_length=8, blank=True)
    acceptance_text_hash = models.CharField(max_length=128)

    class Meta:
        db_table = "booking_policy_acceptances"
        constraints = [
            models.UniqueConstraint(fields=["booking", "checkout_session"], name="uniq_booking_checkout_acceptance"),
        ]
        indexes = [
            models.Index(fields=["booking", "accepted_at"], name="policy_accept_booking_idx"),
            models.Index(fields=["accepted_at"], name="policy_accept_time_idx"),
        ]

    def clean(self):
        _require_aware_utc(self.accepted_at, "accepted_at")

    def save(self, *args, **kwargs):
        if self.accepted_at and timezone.is_aware(self.accepted_at):
            self.accepted_at = self.accepted_at.astimezone(dt_timezone.utc)
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


class ReceiptPDFArtifact(AuditMixin):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        CORRUPTED = "corrupted", "Corrupted"
        ADMIN_REVIEW_REQUIRED = "admin_review_required", "Admin Review Required"

    receipt = models.OneToOneField(BookingReceipt, on_delete=models.PROTECT, related_name="pdf_artifact")
    storage_key = models.CharField(max_length=255, unique=True)
    sha256_hash = models.CharField(max_length=64, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.READY)
    generated_at = models.DateTimeField(null=True, blank=True)
    regeneratable = models.BooleanField(default=False)
    failure_reason_redacted = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "booking_receipt_pdf_artifacts"
        indexes = [
            models.Index(fields=["status", "generated_at"], name="receipt_pdf_status_idx"),
        ]


class BookingNotification(AuditMixin):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RETRY_SCHEDULED = "retry_scheduled", "Retry Scheduled"
        QUOTA_BLOCKED = "quota_blocked", "Quota Blocked"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        FAILED_FINAL = "failed_final", "Failed Final"
        ADMIN_REVIEW_REQUIRED = "admin_review_required", "Admin Review Required"
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
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    scheduled_for = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveSmallIntegerField(default=0)
    failure_code = models.CharField(max_length=64, blank=True)
    last_error_redacted = models.CharField(max_length=255, blank=True)
    provider_message_id_hash = models.CharField(max_length=128, blank=True)
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
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        SKIPPED = "skipped", "Skipped"
        ADMIN_REVIEW_REQUIRED = "admin_review_required", "Admin Review Required"

    class ReminderType(models.TextChoices):
        APPOINTMENT_24H = "appointment_24h", "Appointment 24h"
        APPOINTMENT_2H = "appointment_2h", "Appointment 2h"

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="reminders")
    reminder_type = models.CharField(
        max_length=32,
        choices=ReminderType.choices,
        default=ReminderType.APPOINTMENT_24H,
    )
    channel = models.CharField(max_length=16, choices=Channel.choices)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    failure_reason_redacted = models.CharField(max_length=255, blank=True)
    provider_message_id_hash = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "booking_reminders"
        constraints = [
            models.UniqueConstraint(
                fields=["booking", "reminder_type", "scheduled_for"],
                name="uniq_booking_reminder_schedule",
            ),
        ]
        indexes = [models.Index(fields=["status", "scheduled_for"], name="booking_reminder_due_idx")]

    def clean(self):
        _require_aware_utc(self.scheduled_for, "scheduled_for")
        _require_aware_utc(self.next_attempt_at, "next_attempt_at")
        _require_aware_utc(self.sent_at, "sent_at")


class CustomerOTPChallenge(AuditMixin):
    class Purpose(models.TextChoices):
        RESCHEDULE = "reschedule", "Reschedule"
        RECEIPT_ACCESS = "receipt_access", "Receipt Access"
        CONTACT_UPDATE = "contact_update", "Contact Update"
        PRIVATE_BOOKING_ACCESS = "private_booking_access", "Private Booking Access"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        EXPIRED = "expired", "Expired"
        LOCKED = "locked", "Locked"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, null=True, blank=True, related_name="otp_challenges")
    recipient_type = models.CharField(max_length=16, default="email")
    recipient_hash_hmac = models.CharField(max_length=128, db_index=True)
    otp_hash_hmac = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    request_ip_hash = models.CharField(max_length=128, blank=True)
    user_agent_hash = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = "booking_customer_otp_challenges"
        indexes = [
            models.Index(fields=["recipient_hash_hmac", "purpose", "created_at"], name="booking_otp_recipient_idx"),
            models.Index(fields=["booking", "purpose", "created_at"], name="booking_otp_booking_idx"),
        ]

    def clean(self):
        _require_aware_utc(self.expires_at, "expires_at")
        _require_aware_utc(self.used_at, "used_at")


class CustomerActionSession(AuditMixin):
    class Purpose(models.TextChoices):
        RESCHEDULE = "reschedule", "Reschedule"
        RECEIPT_ACCESS = "receipt_access", "Receipt Access"
        CONTACT_UPDATE = "contact_update", "Contact Update"
        PRIVATE_BOOKING_ACCESS = "private_booking_access", "Private Booking Access"

    token_hash = models.CharField(max_length=128, unique=True)
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="customer_action_sessions")
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking_customer_action_sessions"
        indexes = [models.Index(fields=["booking", "purpose", "expires_at"], name="booking_action_session_idx")]

    def clean(self):
        _require_aware_utc(self.expires_at, "expires_at")
        _require_aware_utc(self.used_at, "used_at")


class GalleryCategory(AuditMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=96)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_sensitive_default = models.BooleanField(default=False)

    class Meta:
        db_table = "gallery_categories"
        ordering = ["sort_order", "name"]
        indexes = [models.Index(fields=["slug", "is_active"], name="gallery_cat_slug_active_idx")]

    def __str__(self):
        return self.name


class GallerySubcategory(AuditMixin):
    class SensitivityDefault(models.TextChoices):
        NORMAL = "normal", "Normal"
        SENSITIVE = "sensitive", "Sensitive"
        RESTRICTED = "restricted", "Restricted"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(GalleryCategory, on_delete=models.PROTECT, related_name="subcategories")
    name = models.CharField(max_length=96)
    slug = models.SlugField(max_length=110)
    description = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sensitivity_default = models.CharField(
        max_length=16,
        choices=SensitivityDefault.choices,
        default=SensitivityDefault.NORMAL,
    )
    requires_warning_default = models.BooleanField(default=False)

    class Meta:
        db_table = "gallery_subcategories"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "slug"], name="uniq_gallery_subcat_slug"),
        ]
        indexes = [models.Index(fields=["category", "slug", "is_active"], name="gallery_subcat_active_idx")]

    def __str__(self):
        return f"{self.category.slug}/{self.slug}"


class GalleryUploadBatch(AuditMixin):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        UPLOADING = "uploading", "Uploading"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="gallery_batches")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATED)
    image_count = models.PositiveSmallIntegerField(default=0)
    total_size_bytes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "gallery_upload_batches"
        indexes = [models.Index(fields=["staff_user", "created_at", "status"], name="gallery_batch_staff_idx")]


class GalleryImage(AuditMixin):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        UPLOADED = "uploaded", "Uploaded"
        QUARANTINED = "quarantined", "Quarantined"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"
        REJECTED = "rejected", "Rejected"
        DELETE_PENDING = "delete_pending", "Delete Pending"
        FAILED = "failed", "Failed"

    class SourceProfile(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        PHONE_STANDARD = "phone_standard", "Phone Standard"
        EDITED_EXPORT = "edited_export", "Edited Export"
        HIGH_RES_CAMERA = "high_res_camera", "High-Resolution Camera"
        COMPRESSED_SOCIAL = "compressed_social", "Compressed Social"

    class Sensitivity(models.TextChoices):
        NORMAL = "normal", "Normal"
        SENSITIVE = "sensitive", "Sensitive"
        RESTRICTED = "restricted", "Restricted"

    class ConsentStatus(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not Required"
        REQUIRED_PENDING = "required_pending", "Required Pending"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    upload_batch = models.ForeignKey(
        GalleryUploadBatch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="images",
    )
    category = models.ForeignKey(GalleryCategory, on_delete=models.PROTECT, related_name="images")
    subcategory = models.ForeignKey(
        GallerySubcategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="images",
    )
    title = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    source_profile = models.CharField(max_length=32, choices=SourceProfile.choices, default=SourceProfile.UNKNOWN)
    sensitivity_level = models.CharField(max_length=16, choices=Sensitivity.choices, default=Sensitivity.NORMAL)
    requires_warning = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    consent_status = models.CharField(
        max_length=24,
        choices=ConsentStatus.choices,
        default=ConsentStatus.NOT_REQUIRED,
    )
    consent_note_redacted = models.CharField(max_length=255, blank=True)
    is_identifiable = models.BooleanField(default=False)
    sensitive_publish_confirmed = models.BooleanField(default=False)
    original_private_key = models.CharField(max_length=255, blank=True)
    quarantine_key = models.CharField(max_length=255, blank=True)
    raw_original_sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    processing_error_code = models.CharField(max_length=64, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="gallery_images")
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    delete_after = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "gallery_images"
        indexes = [
            models.Index(fields=["status", "category", "subcategory"], name="gallery_img_status_cat_idx"),
            models.Index(
                fields=["status", "show_on_homepage", "is_featured", "published_at"], name="gallery_img_home_idx"
            ),
            models.Index(fields=["sensitivity_level", "requires_warning"], name="gallery_img_sensitive_idx"),
            models.Index(fields=["uploaded_by", "created_at"], name="gallery_img_uploader_idx"),
            models.Index(fields=["raw_original_sha256", "status"], name="gallery_img_raw_hash_idx"),
        ]

    def clean(self):
        if self.subcategory and self.category_id and self.subcategory.category_id != self.category_id:
            raise ValidationError({"subcategory": "Subcategory does not belong to category."})
        _require_aware_utc(self.published_at, "published_at")
        _require_aware_utc(self.archived_at, "archived_at")
        _require_aware_utc(self.delete_after, "delete_after")

    def public_payload(self):
        from bookings.gallery.selectors.public_gallery import image_public_payload

        return image_public_payload(self)


class GalleryImageVariant(AuditMixin):
    class VariantType(models.TextChoices):
        THUMBNAIL = "thumbnail", "Thumbnail"
        MOBILE = "mobile", "Mobile"
        TABLET = "tablet", "Tablet"
        DESKTOP = "desktop", "Desktop"
        HERO = "hero", "Hero"
        BLUR_PLACEHOLDER = "blur_placeholder", "Blur Placeholder"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    gallery_image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name="variants")
    variant_type = models.CharField(max_length=32, choices=VariantType.choices)
    storage_key = models.CharField(max_length=255)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    format = models.CharField(max_length=16)
    size_bytes = models.PositiveIntegerField()
    sha256_hash = models.CharField(max_length=64)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "gallery_image_variants"
        constraints = [
            models.UniqueConstraint(fields=["gallery_image", "variant_type"], name="uniq_gallery_variant_type"),
        ]
        indexes = [models.Index(fields=["gallery_image", "variant_type"], name="gallery_variant_type_idx")]


class GalleryAuditLog(AuditMixin):
    class EventType(models.TextChoices):
        UPLOAD_INTENT_CREATED = "upload_intent_created", "Upload Intent Created"
        UPLOADED_TO_QUARANTINE = "uploaded_to_quarantine", "Uploaded To Quarantine"
        PROCESSING_STARTED = "processing_started", "Processing Started"
        PROCESSING_SUCCEEDED = "processing_succeeded", "Processing Succeeded"
        PROCESSING_FAILED = "processing_failed", "Processing Failed"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"
        REPLACED = "replaced", "Replaced"
        DELETED = "deleted", "Deleted"
        REJECTED = "rejected", "Rejected"
        DUPLICATE_REJECTED = "duplicate_rejected", "Duplicate Rejected"
        SENSITIVE_PUBLISH_CONFIRMED = "sensitive_publish_confirmed", "Sensitive Publish Confirmed"
        CONSENT_MARKED = "consent_marked", "Consent Marked"
        CAP_REJECTED = "cap_rejected", "Cap Rejected"
        STORAGE_FAILURE = "storage_failure", "Storage Failure"
        METADATA_REDACTED = "metadata_redacted", "Metadata Redacted"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="gallery_audit_events",
    )
    gallery_image = models.ForeignKey(
        GalleryImage,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    upload_batch = models.ForeignKey(
        GalleryUploadBatch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    event_type = models.CharField(max_length=48, choices=EventType.choices)
    metadata_redacted = models.JSONField(default=dict, blank=True)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "gallery_audit_logs"
        indexes = [models.Index(fields=["event_type", "created_at"], name="gallery_audit_event_idx")]


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


class StaffSecurityAudit(AuditMixin):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILURE = "login_failure", "Login Failure"
        LOGIN_RATE_LIMITED = "login_rate_limited", "Login Rate Limited"
        LOGOUT = "logout", "Logout"
        SESSION_EXPIRED = "session_expired", "Session Expired"
        PASSWORD_RESET_REQUESTED = "password_reset_requested", "Password Reset Requested"
        PASSWORD_RESET_COMPLETED = "password_reset_completed", "Password Reset Completed"
        REAUTH_SUCCESS = "reauth_success", "Reauth Success"
        REAUTH_FAILURE = "reauth_failure", "Reauth Failure"
        CONTACT_REVEAL = "contact_reveal", "Contact Reveal"
        PERMISSION_DENIED = "permission_denied", "Permission Denied"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="staff_security_audits",
    )
    event_type = models.CharField(max_length=64, choices=EventType.choices)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)
    metadata_redacted = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "booking_staff_security_audits"
        indexes = [
            models.Index(fields=["event_type", "created_at"], name="staff_sec_event_time_idx"),
            models.Index(fields=["staff_user", "created_at"], name="staff_sec_user_time_idx"),
        ]


class StaffPasswordResetChallenge(AuditMixin):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        USED = "used", "Used"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="staff_password_reset_challenges",
    )
    email_hash_hmac = models.CharField(max_length=128, db_index=True)
    token_hash_hmac = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "booking_staff_password_reset_challenges"
        indexes = [
            models.Index(fields=["email_hash_hmac", "created_at"], name="staff_reset_email_time_idx"),
            models.Index(fields=["status", "expires_at"], name="staff_reset_status_exp_idx"),
        ]

    def clean(self):
        _require_aware_utc(self.expires_at, "expires_at")
        _require_aware_utc(self.used_at, "used_at")


class PrivacyRightsRequest(AuditMixin):
    """
    Durable GDPR / Kenya DPA 2019 subject-rights ticket.

    Stores peppered contact hashes only — never cleartext email/MSISDN.
    Fulfilment is staff-operated; this row is the audit trail for intake.
    """

    class RequestType(models.TextChoices):
        ACCESS = "access", "Access"
        ERASURE = "erasure", "Erasure"
        RECTIFICATION = "rectification", "Rectification"
        OBJECTION = "objection", "Objection"

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        IN_PROGRESS = "in_progress", "In Progress"
        FULFILLED = "fulfilled", "Fulfilled"
        REJECTED = "rejected", "Rejected"

    ticket_id = models.CharField(max_length=32, unique=True, db_index=True)
    request_type = models.CharField(max_length=32, choices=RequestType.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACCEPTED)
    email_hash_hmac = models.CharField(max_length=128, db_index=True)
    phone_hash_hmac = models.CharField(max_length=128, blank=True, db_index=True)
    details_hash_hmac = models.CharField(max_length=128, blank=True)
    correlation_id = models.CharField(max_length=128, blank=True)
    ip_hash_hmac = models.CharField(max_length=128, blank=True)
    user_agent_hash_hmac = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "booking_privacy_rights_requests"
        indexes = [
            models.Index(fields=["status", "created_at"], name="privacy_rights_status_time_idx"),
            models.Index(fields=["request_type", "created_at"], name="privacy_rights_type_time_idx"),
        ]
