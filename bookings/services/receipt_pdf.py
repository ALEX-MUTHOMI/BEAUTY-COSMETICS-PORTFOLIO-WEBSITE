import re

from django.core.exceptions import ValidationError

from bookings.models import Booking, BookingReceipt
from bookings.services.receipts import render_receipt_payload


def _pdf_escape(value):
    value = re.sub(r"<[^>]*>", "", str(value or ""))
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
        receipt = BookingReceipt.objects.select_related("booking").get(pk=receipt.pk)
        if receipt.booking.status != Booking.Status.CONFIRMED or receipt.payment_status != "paid":
            raise ValidationError("Receipt unavailable.")
        try:
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
        except Exception:
            receipt.pdf_status = BookingReceipt.PdfStatus.FAILED
            receipt.save(update_fields=["pdf_status", "updated_at"])
            raise
        receipt.pdf_status = BookingReceipt.PdfStatus.GENERATED
        receipt.pdf_storage_key = f"generated:{receipt.receipt_number}"
        receipt.save(update_fields=["pdf_status", "pdf_storage_key", "updated_at"])
        return pdf
