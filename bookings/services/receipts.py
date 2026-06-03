import logging
import os
import re
import uuid
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingAuditEvent, BookingNotification, BookingReceipt
from bookings.services.legal import NO_REFUND_NOTICE

NAIROBI = ZoneInfo("Africa/Nairobi")
GENERIC_RECEIPT_ERROR = "Receipt unavailable."
logger = logging.getLogger("bookings.receipts")


def enqueue_receipt_notification_task(notification_id):
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    from bookings.tasks import process_booking_notification

    process_booking_notification.delay(str(notification_id))


def _safe_text(value, max_length=120):
    cleaned = re.sub(r"<[^>]*>", "", str(value or ""))
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", cleaned)
    return " ".join(cleaned.split())[:max_length]


def _receipt_number():
    return f"BPR-{uuid.uuid4().hex[:20].upper()}"


def _receipt_snapshot(booking, session, ledger):
    starts_at = booking.starts_at.astimezone(NAIROBI)
    return {
        "receipt_number": "",
        "booking_reference": str(booking.public_id),
        "service_name": _safe_text(booking.service.name),
        "appointment_starts_at": starts_at.isoformat(),
        "appointment_timezone": "Africa/Nairobi",
        "amount_paid": f"{ledger.amount:.2f}",
        "currency": ledger.currency,
        "payment_method": "M-Pesa",
        "payment_status": "paid",
        "booking_status": Booking.Status.CONFIRMED,
        "paid_at": ledger.credited_at.isoformat() if ledger.credited_at else "",
        "issued_at": timezone.now().isoformat(),
        "client_display_name": _safe_text(booking.customer_profile.full_name_display, 64),
        "redacted_phone": booking.customer_profile.phone_redacted,
        "redacted_email": booking.customer_profile.email_redacted,
        "policy_notice": NO_REFUND_NOTICE,
        "support_contact": "support",
    }


def ensure_confirmation_trust_artifacts_locked(*, booking, checkout_session, billing_ledger):
    if booking.status != Booking.Status.CONFIRMED or billing_ledger.status != LedgerTransaction.Status.SUCCESS:
        raise ValidationError("Receipt cannot be issued for an unconfirmed payment.")

    receipt_number = _receipt_number()
    snapshot = _receipt_snapshot(booking, checkout_session, billing_ledger)
    snapshot["receipt_number"] = receipt_number
    receipt, created = BookingReceipt.objects.get_or_create(
        booking=booking,
        defaults={
            "receipt_number": receipt_number,
            "checkout_session_id": str(checkout_session.id),
            "billing_ledger_id": str(billing_ledger.id),
            "amount": billing_ledger.amount,
            "currency": billing_ledger.currency,
            "payment_method": "M-Pesa",
            "payment_status": "paid",
            "booking_status": booking.status,
            "receipt_snapshot_json_redacted": snapshot,
        },
    )
    if created:
        receipt.issue_download_token()

    notification, notification_created = BookingNotification.objects.get_or_create(
        booking=booking,
        notification_type="booking_confirmed_with_receipt",
        channel=BookingNotification.Channel.EMAIL,
        defaults={
            "receipt": receipt,
            "recipient_email_hash": booking.customer_profile.email_hash_hmac,
            "recipient_email_redacted": booking.customer_profile.email_redacted,
            "status": BookingNotification.Status.PENDING,
            "scheduled_for": timezone.now(),
        },
    )
    if notification_created:
        transaction.on_commit(
            lambda notification_id=str(notification.id): _safe_enqueue_receipt_notification_task(notification_id),
            robust=True,
        )
    return receipt


def _safe_enqueue_receipt_notification_task(notification_id):
    try:
        enqueue_receipt_notification_task(notification_id)
    except Exception:
        logger.warning("booking.receipt_notification.enqueue_failed", extra={"notification_id": str(notification_id)})


def render_receipt_payload(receipt):
    payload = dict(receipt.receipt_snapshot_json_redacted or {})
    payload["receipt_number"] = receipt.receipt_number
    payload["receipt_status"] = "available" if receipt.pdf_status != BookingReceipt.PdfStatus.FAILED else "retry_later"
    return payload


def get_receipt_for_download_token(token):
    token_hash = hash_sensitive_value(token or "")
    receipt = BookingReceipt.objects.filter(
        download_token_hash=token_hash,
        download_token_expires_at__gt=timezone.now(),
    ).first()
    if receipt is None:
        raise ValidationError(GENERIC_RECEIPT_ERROR)
    with transaction.atomic():
        locked = BookingReceipt.objects.select_for_update().get(pk=receipt.pk)
        BookingAuditEvent.objects.create(
            booking=locked.booking,
            old_status=locked.booking.status,
            new_status=locked.booking.status,
            reason="receipt_downloaded",
            actor_type="customer",
            metadata_redacted={"receipt_number": locked.receipt_number},
        )
        return locked


def download_receipt_pdf_for_token(token):
    from bookings.services.receipt_pdf import ReceiptPDFService

    receipt = get_receipt_for_download_token(token)
    return ReceiptPDFService.generate_pdf(receipt)
