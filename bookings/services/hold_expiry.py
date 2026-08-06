import logging

from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingAuditEvent
from bookings.services.calendar_cache import invalidate_calendar_capacity_for_transition

logger = logging.getLogger("bookings.hold_expiry")


class BookingHoldExpiryService:
    """Expire stale holds and bump calendar capacity once per local booking date."""

    @classmethod
    def expire_stale_holds(cls, *, now=None, limit: int = 500, redis_client=None):
        now = now or timezone.now()
        expired_count = 0
        expired_dates: list = []
        with transaction.atomic():
            stale_holds = list(
                Booking.objects.select_for_update(skip_locked=True)
                .filter(status=Booking.Status.HELD, hold_expires_at__lte=now)
                .order_by("hold_expires_at", "id")[:limit]
            )
            for booking in stale_holds:
                old_status = booking.status
                booking.status = Booking.Status.EXPIRED
                booking.save(update_fields=["status", "updated_at"])
                BookingAuditEvent.objects.create(
                    booking=booking,
                    old_status=old_status,
                    new_status=Booking.Status.EXPIRED,
                    reason="hold_expired",
                    actor_type="system",
                    metadata_redacted={"expired_by": "hold_expiry_service"},
                )
                expired_dates.append(booking.local_booking_date)
                expired_count += 1

        # One capacity bump per local day (not per expired row).
        for local_date in sorted({d for d in expired_dates if d is not None}):
            invalidate_calendar_capacity_for_transition(
                old_status=str(Booking.Status.HELD),
                new_status=str(Booking.Status.EXPIRED),
                local_date=local_date,
                redis_client=redis_client,
            )

        if expired_count:
            logger.info("booking.holds.expired", extra={"expired_count": expired_count})
        return expired_count
