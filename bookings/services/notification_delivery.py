import re
from dataclasses import dataclass

from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingNotification
from bookings.services.email_provider import EmailProviderError, get_email_provider, redact_email_error


@dataclass(frozen=True)
class EmailPayload:
    subject: str
    html: str
    text: str
    attachments: list


@dataclass(frozen=True)
class DeliveryResult:
    sent: int = 0
    failed: int = 0
    skipped: int = 0


def _safe_text(value, max_length=160):
    cleaned = re.sub(r"<[^>]*>", "", str(value or ""))
    cleaned = re.sub(r"[\r\n]+", " ", cleaned)
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", cleaned)
    return " ".join(cleaned.split())[:max_length]


def _safe_download_url(receipt):
    return f"https://example.test/receipts/download/{receipt.receipt_number}"


def build_notification_email(notification):
    receipt = notification.receipt
    booking = notification.booking
    snapshot = receipt.receipt_snapshot_json_redacted if receipt else {}
    service_name = _safe_text(snapshot.get("service_name") or booking.service.name)
    booking_ref = str(booking.public_id)
    policy = "No-refund policy applies; contact support for rescheduling."

    if notification.notification_type == "payment_receipt":
        subject = "Payment receipt"
        lines = [
            "Your payment has been received.",
            f"Receipt number: {receipt.receipt_number}",
            f"Booking reference: {booking_ref}",
            f"Amount paid: {snapshot.get('amount_paid')} {snapshot.get('currency')}",
            "Payment method: M-Pesa",
            "Payment status: Paid",
            f"Secure receipt download: {_safe_download_url(receipt)}",
            policy,
        ]
    else:
        subject = "Booking confirmed"
        lines = [
            "Your booking is confirmed and payment has been received.",
            f"Booking reference: {booking_ref}",
            f"Service: {service_name}",
            f"Appointment: {snapshot.get('appointment_starts_at')} Africa/Nairobi",
            "Booking status: Confirmed",
            "Payment status: Paid",
            policy,
        ]
    text = "\n".join(_safe_text(line, 240) for line in lines if line)
    html = "<br>".join(text.splitlines())
    return EmailPayload(subject=subject, html=html, text=text, attachments=[])


class BookingNotificationDeliveryService:
    @classmethod
    def send_pending(cls, *, limit=100):
        sent = failed = skipped = 0
        provider = get_email_provider()
        queryset = (
            BookingNotification.objects.select_related("booking", "booking__customer_profile", "receipt")
            .filter(status=BookingNotification.Status.PENDING)
            .order_by("created_at")[:limit]
        )
        for notification in queryset:
            if not cls._can_send(notification):
                notification.status = BookingNotification.Status.CANCELLED
                notification.last_error_redacted = "delivery skipped"
                notification.save(update_fields=["status", "last_error_redacted", "updated_at"])
                skipped += 1
                continue
            payload = build_notification_email(notification)
            try:
                result = provider.send_email(
                    to_hash=notification.recipient_email_hash,
                    to_redacted=notification.recipient_email_redacted,
                    subject=payload.subject,
                    html=payload.html,
                    text=payload.text,
                    attachments=payload.attachments,
                    metadata={"booking_reference": str(notification.booking.public_id)},
                )
            except EmailProviderError as exc:
                notification.attempts += 1
                notification.status = BookingNotification.Status.FAILED
                notification.last_error_redacted = redact_email_error(exc)
                notification.save(update_fields=["attempts", "status", "last_error_redacted", "updated_at"])
                failed += 1
                continue
            notification.attempts += 1
            notification.status = BookingNotification.Status.SENT
            notification.sent_at = timezone.now()
            notification.provider_message_id_hash = hash_sensitive_value(result.provider_message_id)
            notification.save(update_fields=["attempts", "status", "sent_at", "provider_message_id_hash", "updated_at"])
            sent += 1
        return DeliveryResult(sent=sent, failed=failed, skipped=skipped)

    @staticmethod
    def _can_send(notification):
        booking = notification.booking
        receipt = notification.receipt
        if booking.status != Booking.Status.CONFIRMED:
            return False
        if booking.customer_profile.erased_at:
            return False
        if not receipt or receipt.payment_status != "paid" or receipt.booking_status != Booking.Status.CONFIRMED:
            return False
        return True
