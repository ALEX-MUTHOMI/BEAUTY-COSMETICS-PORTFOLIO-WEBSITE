import hashlib
import os
import re
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, BookingReceipt, ReceiptPDFArtifact
from bookings.services.receipts import render_receipt_payload

BLOCKED_RESOURCE_PATTERN = re.compile(
    r"(?i)(https?://\S+|ftp://\S+|file://\S+|[a-z]:\\[^\s]+|/(?:etc|proc|sys|var|home|root)/[^\s]+)"
)
SENSITIVE_PROVIDER_PATTERN = re.compile(
    r"(?i)\b(raw[-_ ]?receipt[-_\w]*|checkoutrequestid|merchantrequestid|mpesa(?:receipt)?number|ws_co_[\w-]+|mr_[\w-]+)\b"
)


def _pdf_escape(value):
    value = BLOCKED_RESOURCE_PATTERN.sub("[blocked-resource]", str(value or ""))
    value = SENSITIVE_PROVIDER_PATTERN.sub("[redacted-provider-reference]", value)
    value = re.sub(r"(?is)<script.*?>.*?</script>", "", value)
    value = re.sub(r"<[^>]*>", "", value)
    value = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", value)
    return " ".join(value.split())[:180]


def _build_pdf_bytes(lines):
    y = 760
    text_ops = ["BT", "/F1 12 Tf"]
    for line in lines:
        text_ops.append(f"72 {y} Td ({_pdf_escape(line)}) Tj")
        text_ops.append("-72 -18 Td")
        y -= 18
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = sum(len(chunk) for chunk in chunks)
    chunks.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        chunks.append(f"{offset:010d} 00000 n \n".encode())
    chunks.append(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())
    return b"".join(chunks)


class ReceiptPDFService:
    @staticmethod
    def generate_pdf(receipt):
        return ReceiptPDFService.ensure_artifact(receipt)

    @staticmethod
    def ensure_artifact(receipt):
        receipt = BookingReceipt.objects.select_related("booking").get(pk=receipt.pk)
        if receipt.booking.status != Booking.Status.CONFIRMED or receipt.payment_status != "paid":
            raise ValidationError("Receipt unavailable.")
        existing = getattr(receipt, "pdf_artifact", None)
        if existing and existing.status == ReceiptPDFArtifact.Status.READY and not existing.regeneratable:
            try:
                return ReceiptPDFService.read_artifact(existing)
            except ValidationError:
                existing.status = ReceiptPDFArtifact.Status.CORRUPTED
                existing.failure_reason_redacted = "artifact integrity check failed"
                existing.save(update_fields=["status", "failure_reason_redacted", "updated_at"])
        try:
            start = time.monotonic()
            payload = render_receipt_payload(receipt)
            lines = [
                "Booking Payment Receipt",
                f"Receipt number: {payload.get('receipt_number')}",
                f"Booking reference: {payload.get('booking_reference')}",
                f"Service: {payload.get('service_name')}",
                f"Appointment: {payload.get('appointment_starts_at')} Africa/Nairobi",
                f"Amount paid: {payload.get('amount_paid')} {payload.get('currency')}",
                f"Payment method: {payload.get('payment_method')}",
                "Payment status: Paid",
                "Booking status: Confirmed",
                f"Paid at: {payload.get('paid_at')}",
                f"Issued at: {payload.get('issued_at')}",
                f"Client: {payload.get('client_display_name')}",
                f"Phone: {payload.get('redacted_phone')}",
                f"Email: {payload.get('redacted_email')}",
                payload.get("policy_notice", ""),
                f"Support: {payload.get('support_contact')}",
            ]
            pdf = _build_pdf_bytes(lines)
            timeout = float(getattr(settings, "RECEIPT_PDF_TIMEOUT_SECONDS", 5))
            if time.monotonic() - start > timeout:
                raise TimeoutError("PDF generation timeout.")
            max_bytes = int(getattr(settings, "RECEIPT_PDF_MAX_BYTES", 250_000))
            if len(pdf) > max_bytes:
                raise ValidationError("PDF size limit exceeded.")
        except Exception as exc:
            receipt.pdf_status = BookingReceipt.PdfStatus.FAILED
            receipt.save(update_fields=["pdf_status", "updated_at"])
            ReceiptPDFService._record_failed_artifact(receipt, str(exc) or "pdf generation failed")
            raise
        artifact = ReceiptPDFService._store_artifact(receipt, pdf)
        receipt.pdf_status = BookingReceipt.PdfStatus.GENERATED
        receipt.pdf_storage_key = artifact.storage_key
        receipt.save(update_fields=["pdf_status", "pdf_storage_key", "updated_at"])
        return pdf

    @staticmethod
    def _artifact_dir():
        path = getattr(
            settings,
            "RECEIPT_PDF_STORAGE_DIR",
            str(settings.BASE_DIR / ".local" / "receipt_artifacts"),
        )
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def _store_artifact(receipt, pdf):
        digest = hashlib.sha256(pdf).hexdigest()
        storage_key = f"receipt-{receipt.receipt_number}-{digest[:16]}.pdf"
        path = os.path.join(ReceiptPDFService._artifact_dir(), storage_key)
        with open(path, "wb") as handle:
            handle.write(pdf)
        artifact, _created = ReceiptPDFArtifact.objects.update_or_create(
            receipt=receipt,
            defaults={
                "storage_key": storage_key,
                "sha256_hash": digest,
                "size_bytes": len(pdf),
                "status": ReceiptPDFArtifact.Status.READY,
                "generated_at": timezone.now(),
                "regeneratable": False,
                "failure_reason_redacted": "",
            },
        )
        return artifact

    @staticmethod
    def _record_failed_artifact(receipt, reason):
        ReceiptPDFArtifact.objects.update_or_create(
            receipt=receipt,
            defaults={
                "storage_key": f"failed-{receipt.receipt_number}",
                "status": ReceiptPDFArtifact.Status.FAILED,
                "failure_reason_redacted": _pdf_escape(reason).lower(),
                "generated_at": timezone.now(),
            },
        )

    @staticmethod
    def read_artifact(artifact):
        path = os.path.join(ReceiptPDFService._artifact_dir(), os.path.basename(artifact.storage_key))
        try:
            with open(path, "rb") as handle:
                pdf = handle.read()
        except OSError as exc:
            raise ValidationError("Receipt unavailable.") from exc
        digest = hashlib.sha256(pdf).hexdigest()
        if digest != artifact.sha256_hash or len(pdf) != artifact.size_bytes:
            raise ValidationError("Receipt unavailable.")
        return pdf
