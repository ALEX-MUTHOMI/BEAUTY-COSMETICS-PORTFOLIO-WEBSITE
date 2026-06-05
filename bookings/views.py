import re
import uuid
from zoneinfo import ZoneInfo

from django.db.models import Exists, OuterRef, Subquery
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from bookings.models import (
    Booking,
    BookingNotification,
    BookingPolicy,
    BookingReceipt,
    BookingReminder,
    ReceiptPDFArtifact,
)
from bookings.services.legal import NO_REFUND_NOTICE

NAIROBI = ZoneInfo("Africa/Nairobi")
GENERIC_STATUS_UNAVAILABLE = {"detail": "Booking status is unavailable."}
BLOCKED_SURFACE_PATTERN = re.compile(r"(?i)(https?://\S+|ftp://\S+|file://\S+|<[^>]*>)")


def _safe_text(value, max_length=80):
    cleaned = BLOCKED_SURFACE_PATTERN.sub("", str(value or ""))
    cleaned = re.sub(r"[\r\n\x00-\x1f\x7f]+", " ", cleaned)
    return " ".join(cleaned.split())[:max_length]


def _generic_404():
    return JsonResponse(GENERIC_STATUS_UNAVAILABLE, status=404)


def _payment_status(booking):
    if booking.status == Booking.Status.CONFIRMED:
        return "paid"
    if booking.status == Booking.Status.PAYMENT_PENDING:
        return "payment_pending"
    if booking.status == Booking.Status.PAYMENT_FAILED:
        return "payment_failed"
    return "confirming_payment"


def _receipt_status(receipt):
    if receipt is None:
        return "receipt_preparing"
    if receipt.pdf_status == BookingReceipt.PdfStatus.GENERATED:
        return "pdf_generated"
    if receipt.pdf_status == BookingReceipt.PdfStatus.FAILED:
        return "receipt_preparing"
    try:
        artifact = receipt.pdf_artifact
    except ReceiptPDFArtifact.DoesNotExist:
        return "receipt_preparing"
    if artifact.status == ReceiptPDFArtifact.Status.READY:
        return "pdf_generated"
    return "receipt_preparing"


def _email_status(notification):
    notification_status = notification
    if hasattr(notification, "status"):
        notification_status = notification.status
    if notification_status is None:
        return "receipt_email_queued"
    if notification_status == BookingNotification.Status.SENT:
        return "receipt_email_sent"
    if notification_status in {
        BookingNotification.Status.QUOTA_BLOCKED,
        BookingNotification.Status.RETRY_SCHEDULED,
        BookingNotification.Status.FAILED_FINAL,
        BookingNotification.Status.ADMIN_REVIEW_REQUIRED,
    }:
        return "receipt_email_delayed"
    return "receipt_email_queued"


def _next_action(booking, notification):
    notification_status = notification
    if hasattr(notification, "status"):
        notification_status = notification.status
    if booking.status == Booking.Status.CONFIRMED and notification_status != BookingNotification.Status.SENT:
        return "receipt_email_pending"
    if booking.status == Booking.Status.CONFIRMED:
        return "none"
    if booking.status == Booking.Status.PAYMENT_PENDING:
        return "keep_booking_reference"
    if booking.status == Booking.Status.EXPIRED:
        return "select_new_slot"
    return "manual_review_required"


def _reminder_status(booking):
    if hasattr(booking, "_has_pending_reminder"):
        if booking._has_pending_reminder:
            return "scheduled"
        if booking._has_sent_reminder:
            return "sent"
        if booking._has_failed_reminder:
            return "delayed"
        return "not_scheduled"
    reminders = list(booking.reminders.all())
    if not reminders:
        return "not_scheduled"
    if any(reminder.status == BookingReminder.Status.PENDING for reminder in reminders):
        return "scheduled"
    if any(reminder.status == BookingReminder.Status.SENT for reminder in reminders):
        return "sent"
    if any(
        reminder.status in {BookingReminder.Status.FAILED, BookingReminder.Status.ADMIN_REVIEW_REQUIRED}
        for reminder in reminders
    ):
        return "delayed"
    return "not_scheduled"


def _reschedule_payload(booking):
    policy = BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()
    deadline = booking.starts_at - timezone.timedelta(hours=policy.reschedule_cutoff_hours)
    eligible = (
        booking.status == Booking.Status.CONFIRMED
        and booking.reschedule_count < policy.max_reschedules_per_booking
        and timezone.now() < deadline
    )
    return {
        "eligible": bool(eligible),
        "requires_otp": True,
        "deadline_eat": deadline.astimezone(NAIROBI).strftime("%Y-%m-%d %H:%M"),
        "policy": NO_REFUND_NOTICE,
    }


def _status_payload(booking):
    receipt = getattr(booking, "receipt", None)
    notification = getattr(booking, "_receipt_notification_status", None)
    if notification is None and hasattr(booking, "notifications"):
        notification = next(
            (
                candidate
                for candidate in booking.notifications.all()
                if candidate.notification_type == "booking_confirmed_with_receipt"
            ),
            None,
        )
    starts_at = booking.starts_at.astimezone(NAIROBI)
    selection = booking.selection_snapshot_json_redacted or {}
    selection_type = selection.get("type") or booking.booking_type
    if booking.full_package_id:
        service_name = _safe_text(selection.get("name") or booking.full_package.name)
    elif booking.service_id:
        service_name = _safe_text(booking.service.name)
    else:
        service_name = "Selected services"
    duration_minutes = booking.total_duration_minutes
    if not duration_minutes and booking.service_id:
        duration_minutes = booking.service.duration_minutes
    return {
        "booking_reference": str(booking.public_id),
        "booking_status": booking.status,
        "payment_status": _payment_status(booking),
        "receipt_status": _receipt_status(receipt),
        "email_status": _email_status(notification),
        "reminder_status": _reminder_status(booking),
        "reschedule": _reschedule_payload(booking),
        "schedule": {
            "date": starts_at.date().isoformat(),
            "start_time_eat": starts_at.strftime("%I:%M %p"),
            "timezone": "Africa/Nairobi",
            "duration_minutes": duration_minutes,
        },
        "service": {"name": service_name, "selection_type": _safe_text(selection_type, max_length=32)},
        "next_action": _next_action(booking, notification),
    }


@require_GET
def booking_status(request, public_booking_id):
    try:
        public_id = uuid.UUID(str(public_booking_id))
    except (TypeError, ValueError):
        return _generic_404()

    receipt_notification = BookingNotification.objects.filter(
        booking=OuterRef("pk"),
        notification_type="booking_confirmed_with_receipt",
    ).order_by("-created_at")
    reminder_qs = BookingReminder.objects.filter(booking=OuterRef("pk"))
    booking = (
        Booking.objects.select_related("service", "full_package", "receipt", "receipt__pdf_artifact")
        .annotate(
            _receipt_notification_status=Subquery(receipt_notification.values("status")[:1]),
            _has_pending_reminder=Exists(reminder_qs.filter(status=BookingReminder.Status.PENDING)),
            _has_sent_reminder=Exists(reminder_qs.filter(status=BookingReminder.Status.SENT)),
            _has_failed_reminder=Exists(
                reminder_qs.filter(
                    status__in=[
                        BookingReminder.Status.FAILED,
                        BookingReminder.Status.ADMIN_REVIEW_REQUIRED,
                    ]
                )
            ),
        )
        .filter(public_id=public_id)
        .first()
    )
    if booking is None:
        return _generic_404()

    response = JsonResponse(_status_payload(booking))
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
