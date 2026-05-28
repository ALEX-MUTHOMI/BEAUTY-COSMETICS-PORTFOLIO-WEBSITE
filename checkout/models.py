from django.conf import settings
from django.db import models

from core.models import AuditMixin


class CheckoutSession(AuditMixin):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAYMENT_PENDING = "payment_pending", "Payment Pending"
        STK_SENT = "stk_sent", "STK Sent"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="checkout_sessions",
    )
    amount_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    description_snapshot = models.CharField(max_length=255)
    purchasable_type = models.CharField(max_length=64)
    purchasable_id = models.CharField(max_length=128)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    idempotency_key = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "checkout_sessions"
        indexes = [
            models.Index(fields=["customer", "status"], name="checkout_se_customer_b2a808_idx"),
            models.Index(fields=["expires_at"], name="checkout_se_expires_709e52_idx"),
        ]


class CheckoutAttempt(AuditMixin):
    class Provider(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        SENT = "sent", "Sent"
        CALLBACK_RECEIVED = "callback_received", "Callback Received"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        TIMEOUT = "timeout", "Timeout"

    checkout_session = models.ForeignKey(CheckoutSession, on_delete=models.PROTECT, related_name="attempts")
    provider = models.CharField(max_length=32, choices=Provider.choices, default=Provider.MPESA)
    phone_number_hash = models.CharField(max_length=128)
    redacted_phone = models.CharField(max_length=32)
    provider_request_id = models.CharField(max_length=128, unique=True)
    merchant_request_id = models.CharField(max_length=128, unique=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.INITIATED)
    raw_request_hash = models.CharField(max_length=128)
    redacted_request_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "checkout_attempts"
        indexes = [
            models.Index(fields=["provider_request_id"], name="checkout_at_provide_5b9f73_idx"),
            models.Index(fields=["status"], name="checkout_at_status_7b4fc8_idx"),
        ]


class MpesaWebhookInbox(AuditMixin):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        PROCESSED = "processed", "Processed"
        DUPLICATE = "duplicate", "Duplicate"
        REJECTED = "rejected", "Rejected"
        FAILED = "failed", "Failed"

    provider = models.CharField(max_length=32, default="mpesa")
    event_hash = models.CharField(max_length=128, unique=True)
    checkout_request_id_hash = models.CharField(max_length=128, blank=True)
    redacted_payload = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_status = models.CharField(max_length=16, choices=Status.choices, default=Status.RECEIVED)
    correlation_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = "checkout_mpesa_webhook_inbox"
        indexes = [
            models.Index(
                fields=["checkout_request_id_hash"],
                name="checkout_mp_checkou_6bf486_idx",
            ),
            models.Index(fields=["processing_status"], name="checkout_mp_process_f56310_idx"),
        ]
