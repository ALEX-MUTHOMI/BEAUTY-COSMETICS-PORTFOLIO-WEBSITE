from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from billing.exceptions import BillingInvariantError, BillingStateError
from core.models import AuditMixin


class LedgerTransaction(AuditMixin):
    class Direction(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    class Provider(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        INTERNAL = "internal", "Internal"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ledger_transactions",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    direction = models.CharField(
        max_length=16, choices=Direction.choices, default=Direction.CREDIT
    )
    provider = models.CharField(
        max_length=32, choices=Provider.choices, default=Provider.MPESA
    )
    provider_reference_hash = models.CharField(max_length=128, blank=True)
    provider_receipt_hash = models.CharField(max_length=128, blank=True)
    external_correlation_id = models.CharField(max_length=128, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=64, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    raw_payload = models.JSONField(default=dict, blank=True)
    credited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_ledger_transactions"
        constraints = [
            models.UniqueConstraint(
                fields=["checkout_request_id"],
                name="uniq_ledger_checkout_request_id",
            ),
        ]
        indexes = [
            models.Index(
                fields=["checkout_request_id"], name="billing_led_checkou_fa4706_idx"
            ),
            models.Index(
                fields=["provider_reference_hash"],
                name="billing_led_provide_884b14_idx",
            ),
            models.Index(
                fields=["external_correlation_id"],
                name="billing_led_externa_6c94fc_idx",
            ),
            models.Index(fields=["status"], name="billing_led_status_2ca63f_idx"),
        ]

    def clean(self):
        if self.amount < Decimal("0.00"):
            raise ValidationError("Ledger amount cannot be negative.")

    def _assert_update_is_allowed(self):
        if self._state.adding:
            return

        previous = LedgerTransaction.objects.get(pk=self.pk)
        immutable_fields = (
            "amount",
            "currency",
            "direction",
            "provider",
            "provider_reference_hash",
        )
        for field in immutable_fields:
            if getattr(previous, field) != getattr(self, field):
                raise BillingInvariantError(
                    f"{field} is immutable after ledger creation."
                )

        if (
            previous.status == self.Status.SUCCESS
            and previous.provider_receipt_hash != self.provider_receipt_hash
        ):
            raise BillingInvariantError(
                "provider receipt hash is immutable after success."
            )

        allowed = {
            self.Status.PENDING: {
                self.Status.PENDING,
                self.Status.SUCCESS,
                self.Status.FAILED,
            },
            self.Status.SUCCESS: {
                self.Status.SUCCESS,
                self.Status.REVERSED,
                self.Status.REFUNDED,
            },
            self.Status.FAILED: {self.Status.FAILED},
            self.Status.REVERSED: {self.Status.REVERSED},
            self.Status.REFUNDED: {self.Status.REFUNDED},
        }
        if self.status not in allowed[previous.status]:
            raise BillingStateError(
                f"Illegal ledger transition {previous.status} -> {self.status}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self._assert_update_is_allowed()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.checkout_request_id}:{self.status}:{self.amount}"


class FinancialAuditEvent(AuditMixin):
    ledger_transaction = models.ForeignKey(
        LedgerTransaction,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    event_type = models.CharField(max_length=64)
    source = models.CharField(max_length=64, default="system")
    redacted_payload = models.JSONField(default=dict, blank=True)
    payload_hash = models.CharField(max_length=128)
    correlation_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = "billing_financial_audit_events"
        indexes = [
            models.Index(fields=["event_type"], name="billing_fin_event_t_79a315_idx"),
            models.Index(
                fields=["correlation_id"], name="billing_fin_correla_651b38_idx"
            ),
        ]


class SettlementRecord(AuditMixin):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        SETTLED = "settled", "Settled"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    ledger_transaction = models.OneToOneField(
        LedgerTransaction,
        on_delete=models.PROTECT,
        related_name="settlement_record",
    )
    recipient_reference = models.CharField(max_length=128, null=True, blank=True)
    settlement_status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_settlement_records"
        indexes = [
            models.Index(
                fields=["settlement_status"], name="billing_set_settlem_ed3beb_idx"
            )
        ]
