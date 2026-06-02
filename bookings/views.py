import re
import uuid
from zoneinfo import ZoneInfo

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from bookings.models import Booking, BookingNotification, BookingReceipt, ReceiptPDFArtifact

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
    if notification is None:
        return "receipt_email_queued"
    if notification.status == BookingNotification.Status.SENT:
        return "receipt_email_sent"
    if notification.status in {
        BookingNotification.Status.QUOTA_BLOCKED,
        BookingNotification.Status.RETRY_SCHEDULED,
        BookingNotification.Status.FAILED_FINAL,
        BookingNotification.Status.ADMIN_REVIEW_REQUIRED,
    }:
        return "receipt_email_delayed"
    return "receipt_email_queued"


def _next_action(booking, notification):
    if booking.status == Booking.Status.CONFIRMED and (
        notification is None or notification.status != BookingNotification.Status.SENT
    ):
        return "receipt_email_pending"
    if booking.status == Booking.Status.CONFIRMED:
        return "none"
    if booking.status == Booking.Status.PAYMENT_PENDING:
        return "keep_booking_reference"
    if booking.status == Booking.Status.EXPIRED:
        return "select_new_slot"
    return "manual_review_required"


@require_GET
def booking_status(request, public_booking_id):
    try:
        public_id = uuid.UUID(str(public_booking_id))
    except (TypeError, ValueError):
        return _generic_404()

    booking = (
        Booking.objects.select_related("service", "receipt", "receipt__pdf_artifact")
        .prefetch_related("notifications")
        .filter(public_id=public_id)
        .first()
    )
    if booking is None:
        return _generic_404()

    receipt = getattr(booking, "receipt", None)
    notification = next(
        (
            candidate
            for candidate in booking.notifications.all()
            if candidate.notification_type == "booking_confirmed_with_receipt"
        ),
        None,
    )
    starts_at = booking.starts_at.astimezone(NAIROBI)
    payload = {
        "booking_reference": str(booking.public_id),
        "booking_status": booking.status,
        "payment_status": _payment_status(booking),
        "receipt_status": _receipt_status(receipt),
        "email_status": _email_status(notification),
        "schedule": {
            "date": starts_at.date().isoformat(),
            "start_time_eat": starts_at.strftime("%I:%M %p"),
            "duration_minutes": booking.service.duration_minutes,
        },
        "service": {"name": _safe_text(booking.service.name)},
        "next_action": _next_action(booking, notification),
    }
    response = JsonResponse(payload)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
