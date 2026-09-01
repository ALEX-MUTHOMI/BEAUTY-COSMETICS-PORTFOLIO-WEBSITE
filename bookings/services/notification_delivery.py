import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingNotification
from bookings.privacy import decrypt_value, strip_markup
from bookings.services.email_provider import EmailProviderError, get_email_provider, redact_email_error
from bookings.services.legal import NO_REFUND_NOTICE
from bookings.services.receipt_pdf import ReceiptPDFService

logger = logging.getLogger("bookings.notification_delivery")


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
    return strip_markup(value, max_length=max_length)


def _safe_download_url(receipt):
    return f"https://example.test/receipts/download/{receipt.receipt_number}"


def resolve_notification_recipient_email(notification):
    """Decrypt customer email at send boundary. Fail-closed if unavailable."""
    profile = getattr(notification.booking, "customer_profile", None)
    if profile is None or not getattr(profile, "email_encrypted", ""):
        raise EmailProviderError("Recipient email address is unavailable for delivery.")
    try:
        email = decrypt_value(profile.email_encrypted)
    except Exception as exc:  # noqa: BLE001 - fail closed on any decrypt/crypto error
        raise EmailProviderError("Recipient email address is unavailable for delivery.") from exc
    email = str(email or "").strip().lower()
    if not email or "@" not in email or "***" in email:
        raise EmailProviderError("Recipient email address is unavailable for delivery.")
    return email


def _attachment_for_receipt(receipt):
    try:
        artifact = receipt.pdf_artifact
    except Exception:
        return []
    if artifact.status != artifact.Status.READY:
        return []
    pdf = ReceiptPDFService.read_artifact(artifact)
    return [
        {
            "filename": f"receipt-{receipt.receipt_number}.pdf",
            "content": pdf,
            "content_type": "application/pdf",
            "sha256": artifact.sha256_hash,
            "size_bytes": artifact.size_bytes,
        }
    ]


def build_notification_email(notification):
    receipt = notification.receipt
    booking = notification.booking
    snapshot = receipt.receipt_snapshot_json_redacted if receipt else {}
    service_name = _safe_text(snapshot.get("service_name") or booking.service.name)
    booking_ref = str(booking.public_id)
    policy = NO_REFUND_NOTICE

    subject = "Booking confirmed and payment received"
    lines = [
        "Your booking is confirmed and payment has been received.",
        f"Receipt number: {receipt.receipt_number}",
        f"Booking reference: {booking_ref}",
        f"Service: {service_name}",
        f"Appointment: {snapshot.get('appointment_starts_at')} Africa/Nairobi",
        f"Amount paid: {snapshot.get('amount_paid')} {snapshot.get('currency')}",
        "Payment method: M-Pesa",
        "Booking status: Confirmed",
        "Payment status: Paid",
        "Your PDF receipt is attached.",
        policy,
    ]
    text = "\n".join(_safe_text(line, 240) for line in lines if line)
    html = "<br>".join(text.splitlines())
    return EmailPayload(subject=subject, html=html, text=text, attachments=_attachment_for_receipt(receipt))


def _counter_key(kind, provider, window):
    return f"provider:email:{kind}:{provider}:{window}"


def _today():
    return timezone.now().date().isoformat()


def _month():
    now = timezone.now()
    return f"{now.year:04d}-{now.month:02d}"


def _increment_counter(kind, provider):
    day_key = _counter_key(kind, provider, f"day:{_today()}")
    month_key = _counter_key(kind, provider, f"month:{_month()}")
    day_value = cache.get(day_key, 0) + 1
    month_value = cache.get(month_key, 0) + 1
    cache.set(day_key, day_value, 60 * 60 * 48)
    cache.set(month_key, month_value, 60 * 60 * 24 * 45)
    return day_value, month_value


def _sent_count(provider):
    return cache.get(_counter_key("sent", provider, f"day:{_today()}"), 0)


def _emit_quota_alert(event, provider, **extra):
    safe = {"provider": provider, **{key: value for key, value in extra.items() if isinstance(value, (int, str))}}
    logger.warning(event, extra=safe)


def _max_attempts():
    return int(getattr(settings, "EMAIL_NOTIFICATION_MAX_ATTEMPTS", 3))


def _retry_delay_seconds(attempts):
    return min(3600, 60 * (2 ** max(0, attempts - 1)))


def _is_rate_limit_error(error):
    surface = str(error).lower()
    return "429" in surface or "quota" in surface or "rate" in surface


def _failure_code_for_exception(error):
    surface = str(error).lower()
    if (
        isinstance(error, PermissionError)
        or "permission denied" in surface
        or "storage is not writable" in surface
        or "storage_unwritable" in surface
        or "errno 13" in surface
    ):
        return "storage_unwritable"
    if "pdf" in surface or "receipt" in surface or "artifact" in surface:
        return "pdf_artifact_unavailable"
    if _is_rate_limit_error(error):
        return "email_provider_rate_limited"
    return "email_provider_failure"


def get_backup_email_provider():
    return None


def notification_backlog_summary():
    pending = BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count()
    retry = BookingNotification.objects.filter(status=BookingNotification.Status.RETRY_SCHEDULED).count()
    quota = BookingNotification.objects.filter(status=BookingNotification.Status.QUOTA_BLOCKED).count()
    failed = BookingNotification.objects.filter(status=BookingNotification.Status.FAILED_FINAL).count()
    oldest = (
        BookingNotification.objects.filter(
            status__in=[
                BookingNotification.Status.PENDING,
                BookingNotification.Status.RETRY_SCHEDULED,
                BookingNotification.Status.QUOTA_BLOCKED,
            ]
        )
        .order_by("created_at")
        .first()
    )
    return {
        "pending": pending,
        "retry_scheduled": retry,
        "quota_blocked": quota,
        "failed_final": failed,
        "oldest_pending_seconds": int((timezone.now() - oldest.created_at).total_seconds()) if oldest else 0,
    }


class BookingNotificationDeliveryService:
    @classmethod
    def send_one(cls, notification_id):
        notification = BookingNotification.objects.filter(pk=notification_id).first()
        if notification is None:
            return DeliveryResult(skipped=1)
        return cls._send_notifications([notification])

    @classmethod
    def send_pending(cls, *, limit=100):
        queryset = (
            BookingNotification.objects.select_related("booking", "booking__customer_profile", "receipt")
            .filter(
                status__in=[
                    BookingNotification.Status.PENDING,
                    BookingNotification.Status.RETRY_SCHEDULED,
                    BookingNotification.Status.QUOTA_BLOCKED,
                ],
                scheduled_for__lte=timezone.now(),
            )
            .order_by("created_at")[:limit]
        )
        return cls._send_notifications(list(queryset))

    @classmethod
    def _send_notifications(cls, notifications):
        sent = failed = skipped = 0
        provider = get_email_provider()
        provider_name = getattr(provider, "provider", "unknown")
        for notification in notifications:
            with transaction.atomic():
                notification = BookingNotification.objects.select_for_update().get(pk=notification.pk)
                if notification.status == BookingNotification.Status.SENT:
                    skipped += 1
                    continue
            if not cls._can_send(notification):
                notification.status = BookingNotification.Status.CANCELLED
                notification.failure_code = "notification_not_sendable"
                notification.last_error_redacted = "delivery skipped"
                notification.save(update_fields=["status", "failure_code", "last_error_redacted", "updated_at"])
                skipped += 1
                continue
            try:
                ReceiptPDFService.ensure_artifact(notification.receipt)
                payload = build_notification_email(notification)
                if not payload.attachments:
                    raise EmailProviderError("receipt PDF artifact unavailable")
            except Exception as exc:
                cls._mark_retry_or_final(notification, exc)
                failed += 1
                continue
            if cls._quota_blocks_send(notification, provider_name):
                failed += 1
                continue
            try:
                recipient_email = resolve_notification_recipient_email(notification)
                result = provider.send_email(
                    to_hash=notification.recipient_email_hash,
                    to_redacted=notification.recipient_email_redacted,
                    to_address=recipient_email,
                    subject=payload.subject,
                    html=payload.html,
                    text=payload.text,
                    attachments=payload.attachments,
                    metadata={"booking_reference": str(notification.booking.public_id)},
                )
            except EmailProviderError as exc:
                if _is_rate_limit_error(exc):
                    _increment_counter("rate_limited", provider_name)
                    _emit_quota_alert("email.provider.rate_limited", provider_name)
                cls._mark_retry_or_final(notification, exc)
                failed += 1
                continue
            notification.attempts += 1
            notification.status = BookingNotification.Status.SENT
            notification.failure_code = ""
            notification.last_error_redacted = ""
            notification.sent_at = timezone.now()
            notification.provider_message_id_hash = hash_sensitive_value(result.provider_message_id)
            notification.save(
                update_fields=[
                    "attempts",
                    "status",
                    "failure_code",
                    "last_error_redacted",
                    "sent_at",
                    "provider_message_id_hash",
                    "updated_at",
                ]
            )
            day_count, month_count = _increment_counter("sent", provider_name)
            if day_count >= int(getattr(settings, "EMAIL_DAILY_SOFT_LIMIT", 80)):
                _emit_quota_alert("email.quota.soft_limit_reached", provider_name, day_count=day_count)
            if month_count >= int(getattr(settings, "EMAIL_MONTHLY_SOFT_LIMIT", 2500)):
                _emit_quota_alert("email.quota.monthly_soft_limit_reached", provider_name, month_count=month_count)
            sent += 1
        summary = notification_backlog_summary()
        if summary["pending"] + summary["retry_scheduled"] + summary["quota_blocked"] > int(
            getattr(settings, "EMAIL_BACKLOG_HIGH_WATERMARK", 100)
        ):
            _emit_quota_alert(
                "email.notification.backlog_high",
                provider_name,
                pending=summary["pending"],
                retry_scheduled=summary["retry_scheduled"],
                quota_blocked=summary["quota_blocked"],
            )
        return DeliveryResult(sent=sent, failed=failed, skipped=skipped)

    @staticmethod
    def _quota_blocks_send(notification, provider_name):
        sent_count = _sent_count(provider_name)
        hard_limit = int(getattr(settings, "EMAIL_DAILY_HARD_LIMIT", 100))
        if sent_count < hard_limit:
            return False
        notification.status = BookingNotification.Status.QUOTA_BLOCKED
        notification.failure_code = "email_quota_hard_limit"
        notification.last_error_redacted = "provider quota window reached"
        notification.scheduled_for = timezone.now() + timezone.timedelta(hours=24)
        notification.save(
            update_fields=["status", "failure_code", "last_error_redacted", "scheduled_for", "updated_at"]
        )
        _increment_counter("failed", provider_name)
        _emit_quota_alert("email.quota.hard_limit_reached", provider_name, day_count=sent_count)
        if getattr(settings, "EMAIL_BACKUP_PROVIDER_ENABLED", False):
            backup = get_backup_email_provider()
            if backup is None:
                _emit_quota_alert("email.notification.dlq_required", provider_name)
        return True

    @staticmethod
    def _mark_retry_or_final(notification, exc):
        notification.attempts += 1
        notification.failure_code = _failure_code_for_exception(exc)
        notification.last_error_redacted = redact_email_error(exc)
        if notification.attempts >= _max_attempts():
            notification.status = BookingNotification.Status.FAILED_FINAL
            _emit_quota_alert("email.notification.dlq_required", "email", pending=1)
        else:
            notification.status = BookingNotification.Status.RETRY_SCHEDULED
            notification.scheduled_for = timezone.now() + timezone.timedelta(
                seconds=_retry_delay_seconds(notification.attempts)
            )
        notification.save(
            update_fields=[
                "attempts",
                "status",
                "scheduled_for",
                "failure_code",
                "last_error_redacted",
                "updated_at",
            ]
        )

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
