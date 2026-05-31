from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingAuditEvent


class BookingStateError(Exception):
    pass


VALID_TRANSITIONS = {
    Booking.Status.REQUESTED: {Booking.Status.HELD},
    Booking.Status.HELD: {Booking.Status.PAYMENT_PENDING, Booking.Status.EXPIRED},
    Booking.Status.PAYMENT_PENDING: {Booking.Status.CONFIRMED, Booking.Status.PAYMENT_FAILED},
    Booking.Status.CONFIRMED: {
        Booking.Status.RESCHEDULE_REQUESTED,
        Booking.Status.CHECKED_IN,
        Booking.Status.LATE,
        Booking.Status.NO_SHOW,
        Booking.Status.CANCELLED_BY_CLIENT,
        Booking.Status.CANCELLED_BY_BUSINESS,
    },
    Booking.Status.RESCHEDULE_REQUESTED: {Booking.Status.RESCHEDULE_HELD},
    Booking.Status.RESCHEDULE_HELD: {Booking.Status.RESCHEDULED},
    Booking.Status.RESCHEDULED: {Booking.Status.CONFIRMED},
    Booking.Status.LATE: {Booking.Status.CHECKED_IN, Booking.Status.NO_SHOW},
    Booking.Status.CHECKED_IN: {Booking.Status.IN_PROGRESS},
    Booking.Status.IN_PROGRESS: {Booking.Status.COMPLETED},
}
# This table is the only sanctioned booking lifecycle path. Terminal payment
# and cancellation states cannot be promoted without a future audited correction
# workflow.


def _validate_transition(booking, new_status):
    allowed = VALID_TRANSITIONS.get(booking.status, set())
    if new_status not in allowed:
        raise BookingStateError(f"Illegal booking transition {booking.status} -> {new_status}.")
    # No-show is a staff action with customer impact, so the grace window is
    # enforced in the transition service instead of a view.
    if new_status == Booking.Status.NO_SHOW and timezone.now() < booking.starts_at + timedelta(minutes=30):
        raise BookingStateError("No-show cannot be recorded before the grace period ends.")


def transition_booking(booking, new_status, actor_type, reason="", actor_id=None, request_id=None, metadata=None):
    with transaction.atomic():
        locked = Booking.objects.select_for_update().get(pk=booking.pk)
        old_status = locked.status
        _validate_transition(locked, new_status)
        locked.status = new_status
        if new_status == Booking.Status.CONFIRMED and locked.confirmed_at is None:
            locked.confirmed_at = timezone.now()
        if new_status == Booking.Status.NO_SHOW:
            locked.no_show_at = timezone.now()
        locked.save()
        BookingAuditEvent.objects.create(
            booking=locked,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            actor_type=actor_type,
            actor_id=actor_id,
            request_id=request_id,
            metadata_redacted=metadata or {},
        )
        booking.status = locked.status
        return locked
