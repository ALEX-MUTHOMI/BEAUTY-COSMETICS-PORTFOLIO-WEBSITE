from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from bookings.models import BookingRescheduleRequest


def create_reschedule_request(
    booking,
    requested_starts_at,
    requested_ends_at,
    reason="",
    original_billing_ledger_id="",
    additional_fee_amount="0.00",
    new_checkout_session_id="",
):
    return BookingRescheduleRequest.objects.create(
        booking=booking,
        requested_starts_at=requested_starts_at,
        requested_ends_at=requested_ends_at,
        expires_at=timezone.now() + timedelta(minutes=booking.service.duration_minutes),
        reason=reason[:255],
        original_billing_ledger_id=original_billing_ledger_id,
        additional_fee_amount=Decimal(str(additional_fee_amount)),
        new_checkout_session_id=new_checkout_session_id,
    )
