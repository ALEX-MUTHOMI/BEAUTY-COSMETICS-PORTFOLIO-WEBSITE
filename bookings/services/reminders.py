from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingReminder
from bookings.services.email_provider import EmailProviderError, get_email_provider, redact_email_error


@dataclass(frozen=True)
class ReminderDeliveryResult:
    sent: int = 0
    failed: int = 0
    skipped: int = 0


def _send_2h_enabled():
    return str(getattr(settings, "BOOKING_REMINDER_2H_ENABLED", "false")).lower() in {"true", "1", "t"}


def _retry_delay_seconds(attempts):
    return min(3600, 60 * (2 ** max(0, attempts - 1)))


def _max_attempts():
    return int(getattr(settings, "BOOKING_REMINDER_MAX_ATTEMPTS", 3))


def create_pending_reminder(
    booking,
    channel,
    scheduled_for,
    reminder_type=BookingReminder.ReminderType.APPOINTMENT_24H,
):
    reminder, _created = BookingReminder.objects.get_or_create(
        booking=booking,
        reminder_type=reminder_type,
        scheduled_for=scheduled_for,
        defaults={
            "channel": channel,
            "status": BookingReminder.Status.PENDING,
        },
    )
    return reminder


def schedule_booking_reminders(booking):
    booking = Booking.objects.select_related("customer_profile").get(pk=booking.pk)
    if booking.status != Booking.Status.CONFIRMED or booking.customer_profile.erased_at:
        return []
    now = timezone.now()
    if booking.starts_at <= now:
        return []
    candidates = [
        (
            BookingReminder.ReminderType.APPOINTMENT_24H,
            booking.starts_at - timezone.timedelta(hours=24),
        )
    ]
    if _send_2h_enabled():
        candidates.append(
            (BookingReminder.ReminderType.APPOINTMENT_2H, booking.starts_at - timezone.timedelta(hours=2))
        )

    created = []
    for reminder_type, scheduled_for in candidates:
        if scheduled_for <= now:
            scheduled_for = now
        reminder, was_created = BookingReminder.objects.get_or_create(
            booking=booking,
            reminder_type=reminder_type,
            scheduled_for=scheduled_for,
            defaults={
                "channel": BookingReminder.Channel.EMAIL,
                "status": BookingReminder.Status.PENDING,
            },
        )
        if was_created:
            created.append(reminder)
    return created


def cancel_pending_reminders(booking):
    return booking.reminders.filter(status=BookingReminder.Status.PENDING).update(
        status=BookingReminder.Status.CANCELLED
    )


def reminder_is_sendable(reminder):
    if reminder.booking.customer_profile.erased_at:
        return False
    if reminder.booking.status != Booking.Status.CONFIRMED:
        return False
    return reminder.status == BookingReminder.Status.PENDING and reminder.booking.customer_profile.reminder_consent


def _safe_email_payload(reminder):
    booking = reminder.booking
    local_start = booking.starts_at.astimezone(timezone.get_fixed_timezone(180))
    selection = booking.selection_snapshot_json_redacted or {}
    service_name = selection.get("name")
    if not service_name and booking.service_id:
        service_name = booking.service.name
    if not service_name and booking.full_package_id:
        service_name = booking.full_package.name
    service_name = str(service_name or "Selected services")[:80]
    text = "\n".join(
        [
            "Appointment reminder.",
            f"Booking reference: {booking.public_id}",
            f"Service: {service_name}",
            f"Appointment: {local_start:%Y-%m-%d %I:%M %p} Africa/Nairobi",
            "Paid bookings are not refundable. Rescheduling is available according to policy.",
        ]
    )
    return {
        "to_hash": booking.customer_profile.email_hash_hmac,
        "to_redacted": booking.customer_profile.email_redacted,
        "subject": "Appointment reminder",
        "html": "<br>".join(text.splitlines()),
        "text": text,
        "attachments": [],
        "metadata": {"booking_reference": str(booking.public_id), "notification_type": reminder.reminder_type},
    }


class BookingReminderDeliveryService:
    @classmethod
    def send_due(cls, *, now=None, limit=100):
        now = now or timezone.now()
        reminders = list(
            BookingReminder.objects.select_related(
                "booking",
                "booking__customer_profile",
                "booking__service",
                "booking__full_package",
            )
            .filter(
                status=BookingReminder.Status.PENDING,
                scheduled_for__lte=now,
            )
            .order_by("scheduled_for")[:limit]
        )
        sent = failed = skipped = 0
        provider = get_email_provider()
        for reminder in reminders:
            with transaction.atomic():
                locked = (
                    BookingReminder.objects.select_for_update(of=("self",))
                    .select_related(
                        "booking",
                        "booking__customer_profile",
                        "booking__service",
                        "booking__full_package",
                    )
                    .get(pk=reminder.pk)
                )
                if locked.status != BookingReminder.Status.PENDING:
                    skipped += 1
                    continue
                if not reminder_is_sendable(locked):
                    locked.status = BookingReminder.Status.SKIPPED
                    locked.failure_reason_redacted = "reminder not sendable"
                    locked.save(update_fields=["status", "failure_reason_redacted", "updated_at"])
                    skipped += 1
                    continue
                locked.status = BookingReminder.Status.SENDING
                locked.save(update_fields=["status", "updated_at"])

            try:
                result = provider.send_email(**_safe_email_payload(locked))
            except EmailProviderError as exc:
                locked.attempts += 1
                locked.status = (
                    BookingReminder.Status.ADMIN_REVIEW_REQUIRED
                    if locked.attempts >= _max_attempts()
                    else BookingReminder.Status.PENDING
                )
                locked.next_attempt_at = timezone.now() + timezone.timedelta(
                    seconds=_retry_delay_seconds(locked.attempts)
                )
                locked.failure_reason_redacted = redact_email_error(exc)
                locked.save(
                    update_fields=[
                        "attempts",
                        "status",
                        "next_attempt_at",
                        "failure_reason_redacted",
                        "updated_at",
                    ]
                )
                failed += 1
                continue

            locked.status = BookingReminder.Status.SENT
            locked.sent_at = timezone.now()
            locked.provider_message_id_hash = hash_sensitive_value(getattr(result, "provider_message_id", ""))[:128]
            locked.failure_reason_redacted = ""
            locked.save(
                update_fields=[
                    "status",
                    "sent_at",
                    "provider_message_id_hash",
                    "failure_reason_redacted",
                    "updated_at",
                ]
            )
            sent += 1
        return ReminderDeliveryResult(sent=sent, failed=failed, skipped=skipped)
