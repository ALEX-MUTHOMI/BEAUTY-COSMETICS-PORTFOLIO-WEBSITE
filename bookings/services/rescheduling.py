import re
from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking, BookingAuditEvent, BookingPolicy, BookingRescheduleRequest, CustomerActionSession
from bookings.privacy import strip_markup
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.reminders import cancel_pending_reminders, schedule_booking_reminders

NAIROBI = ZoneInfo("Africa/Nairobi")
GENERIC_RESCHEDULE_ERROR = "Unable to reschedule booking."


def _safe_reason(reason):
    cleaned = strip_markup(reason, max_length=255)
    cleaned = re.sub(r"(?i)refund", "policy", cleaned)
    return cleaned


def _policy():
    return BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()


def _normalize_start(value):
    if value is None or timezone.is_naive(value):
        raise ValidationError(GENERIC_RESCHEDULE_ERROR)
    return value.astimezone(ZoneInfo("UTC")).replace(second=0, microsecond=0)


def _validate_policy(booking, requested_starts_at, policy):
    local_start = requested_starts_at.astimezone(NAIROBI)
    if timezone.now() > booking.starts_at - timedelta(hours=policy.reschedule_cutoff_hours):
        raise ValidationError(GENERIC_RESCHEDULE_ERROR)
    if booking.reschedule_count >= policy.max_reschedules_per_booking:
        raise ValidationError(GENERIC_RESCHEDULE_ERROR)
    if local_start.weekday() == 6:
        raise ValidationError(GENERIC_RESCHEDULE_ERROR)
    if not (7 <= local_start.hour < 19):
        raise ValidationError(GENERIC_RESCHEDULE_ERROR)


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
        reason=_safe_reason(reason),
        original_billing_ledger_id=original_billing_ledger_id,
        additional_fee_amount=Decimal(str(additional_fee_amount)),
        new_checkout_session_id=new_checkout_session_id,
    )


class BookingRescheduleService:
    @classmethod
    def reschedule(cls, *, booking_public_id, action_token, requested_starts_at, reason=""):
        try:
            with transaction.atomic():
                booking = (
                    Booking.objects.select_for_update(of=("self",))
                    .select_related("service", "resource", "customer_profile")
                    .get(public_id=booking_public_id)
                )
                session = CustomerOTPService.consume_action_session(
                    token=action_token,
                    booking=booking,
                    purpose=CustomerActionSession.Purpose.RESCHEDULE,
                )
                if session is None:
                    raise ValidationError(GENERIC_RESCHEDULE_ERROR)
                if booking.status != Booking.Status.CONFIRMED:
                    raise ValidationError(GENERIC_RESCHEDULE_ERROR)

                starts_at = _normalize_start(requested_starts_at)
                ends_at = starts_at + timedelta(minutes=booking.service.duration_minutes)
                policy = _policy()
                _validate_policy(booking, starts_at, policy)

                original_starts_at = booking.starts_at
                original_ends_at = booking.ends_at
                reschedule_request = create_reschedule_request(
                    booking=booking,
                    requested_starts_at=starts_at,
                    requested_ends_at=ends_at,
                    reason=reason,
                )

                booking.starts_at = starts_at
                booking.ends_at = ends_at
                booking.reschedule_count += 1
                booking.status = Booking.Status.CONFIRMED
                booking.save(update_fields=["starts_at", "ends_at", "reschedule_count", "status", "updated_at"])

                reschedule_request.status = BookingRescheduleRequest.Status.ACCEPTED
                reschedule_request.save(update_fields=["status", "updated_at"])
                cancel_pending_reminders(booking)
                schedule_booking_reminders(booking)
                BookingAuditEvent.objects.create(
                    booking=booking,
                    old_status=Booking.Status.CONFIRMED,
                    new_status=Booking.Status.CONFIRMED,
                    reason="customer_rescheduled",
                    actor_type="customer",
                    metadata_redacted={
                        "old_date": original_starts_at.date().isoformat(),
                        "new_date": starts_at.date().isoformat(),
                        "old_time": original_starts_at.astimezone(NAIROBI).strftime("%H:%M"),
                        "new_time": starts_at.astimezone(NAIROBI).strftime("%H:%M"),
                        "original_duration_minutes": int((original_ends_at - original_starts_at).total_seconds() / 60),
                    },
                )
                return booking
        except (Booking.DoesNotExist, IntegrityError, ValueError, TypeError) as exc:
            raise ValidationError(GENERIC_RESCHEDULE_ERROR) from exc

    @classmethod
    def staff_reschedule(cls, *, booking_public_id, requested_starts_at, reason="", actor_user=None):
        """Move a confirmed booking from the staff desk (no customer OTP)."""
        try:
            with transaction.atomic():
                booking = (
                    Booking.objects.select_for_update(of=("self",))
                    .select_related("service", "resource", "customer_profile")
                    .get(public_id=booking_public_id)
                )
                if booking.status not in {
                    Booking.Status.CONFIRMED,
                    Booking.Status.RESCHEDULE_REQUESTED,
                }:
                    raise ValidationError(GENERIC_RESCHEDULE_ERROR)

                starts_at = _normalize_start(requested_starts_at)
                ends_at = starts_at + timedelta(minutes=booking.service.duration_minutes)
                policy = _policy()
                _validate_policy(booking, starts_at, policy)

                original_starts_at = booking.starts_at
                original_ends_at = booking.ends_at
                reschedule_request = create_reschedule_request(
                    booking=booking,
                    requested_starts_at=starts_at,
                    requested_ends_at=ends_at,
                    reason=reason or "staff_desk_move",
                )

                booking.starts_at = starts_at
                booking.ends_at = ends_at
                booking.reschedule_count += 1
                booking.status = Booking.Status.CONFIRMED
                booking.save(update_fields=["starts_at", "ends_at", "reschedule_count", "status", "updated_at"])

                reschedule_request.status = BookingRescheduleRequest.Status.ACCEPTED
                reschedule_request.save(update_fields=["status", "updated_at"])
                cancel_pending_reminders(booking)
                schedule_booking_reminders(booking)
                actor_email = getattr(actor_user, "email", "") or ""
                BookingAuditEvent.objects.create(
                    booking=booking,
                    old_status=Booking.Status.CONFIRMED,
                    new_status=Booking.Status.CONFIRMED,
                    reason="staff_rescheduled",
                    actor_type="staff",
                    metadata_redacted={
                        "old_date": original_starts_at.date().isoformat(),
                        "new_date": starts_at.date().isoformat(),
                        "old_time": original_starts_at.astimezone(NAIROBI).strftime("%H:%M"),
                        "new_time": starts_at.astimezone(NAIROBI).strftime("%H:%M"),
                        "original_duration_minutes": int((original_ends_at - original_starts_at).total_seconds() / 60),
                        "actor_email_domain": actor_email.split("@")[-1] if "@" in actor_email else "",
                    },
                )
                return booking
        except (Booking.DoesNotExist, IntegrityError, ValueError, TypeError) as exc:
            raise ValidationError(GENERIC_RESCHEDULE_ERROR) from exc
