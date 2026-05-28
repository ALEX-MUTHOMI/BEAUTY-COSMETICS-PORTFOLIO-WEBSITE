from datetime import datetime, timedelta

from django.conf import settings
from django.db import models

from core.models import AuditMixin


class Booking(AuditMixin):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings"
    )
    service_name = models.CharField(max_length=128, default="Beauty consultation")
    beautician_name = models.CharField(max_length=128, default="Assigned beautician")
    beautician_payout_phone = models.CharField(max_length=15, default="+254700000000")
    service_date = models.DateField()
    time_slot = models.CharField(max_length=16)
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    ledger_transaction = models.OneToOneField(
        "billing.LedgerTransaction",
        on_delete=models.PROTECT,
        related_name="booking",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING_PAYMENT
    )
    paid_to_beautician_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "bookings"
        constraints = [
            models.UniqueConstraint(
                fields=["service_date", "time_slot"],
                name="uniq_booking_service_date_time_slot",
            ),
        ]
        indexes = [
            models.Index(
                fields=["service_date", "time_slot"], name="bookings_service_f1f4bf_idx"
            ),
            models.Index(fields=["status"], name="bookings_status_595c9d_idx"),
        ]

    def __str__(self):
        return f"{self.service_date} {self.time_slot} {self.status}"

    @property
    def duration(self):
        return timedelta(minutes=self.duration_minutes)

    @property
    def starts_at(self):
        return datetime.combine(
            self.service_date, datetime.strptime(self.time_slot, "%H:%M").time()
        )

    @property
    def ends_at(self):
        return self.starts_at + self.duration
