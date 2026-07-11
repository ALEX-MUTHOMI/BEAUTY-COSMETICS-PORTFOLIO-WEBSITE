import pytest
from django.core.cache import cache
from django.test import Client

from bookings.infrastructure.receipt_pdf import ReceiptPDFService
from bookings.models import BookingReceipt, StaffActionAuditEvent, StaffSecurityAudit
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
from bookings.tests.test_staff_portal_helpers import staff_login, staff_payment_url


def staff_receipt_url(booking):
    return f"/api/staff/bookings/{booking.public_id}/receipt.pdf"


@pytest.mark.django_db(transaction=True)
def test_staff_receipt_pdf_permission_missing_receipt_and_happy_path(settings, tmp_path, monkeypatch):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    cache.clear()
    booking, _session, _ledger = _confirm_paid_booking("staff-receipt-pdf")

    denied = Client()
    staff_login(denied, permissions=["view_staff_booking"])
    assert denied.get(staff_receipt_url(booking), secure=True).status_code == 403

    from bookings.tests.test_booking_checkout_contract import _held_booking

    missing = Client()
    staff_login(missing, permissions=["view_staff_payment_summary"])
    unpaid = _held_booking(key="staff-receipt-missing")
    assert missing.get(staff_receipt_url(unpaid), secure=True).status_code == 404

    booking, _session, _ledger = _confirm_paid_booking("staff-receipt-pdf-ok")
    ReceiptPDFService.ensure_artifact(booking.receipt)

    generate_calls = {"count": 0}
    original_ensure = ReceiptPDFService.ensure_artifact

    def counting_ensure(receipt):
        generate_calls["count"] += 1
        return original_ensure(receipt)

    monkeypatch.setattr(ReceiptPDFService, "ensure_artifact", staticmethod(counting_ensure))

    permitted = Client()
    staff_login(permitted, permissions=["view_staff_booking", "view_staff_payment_summary"])
    first = permitted.get(staff_receipt_url(booking), secure=True)
    second = permitted.get(staff_receipt_url(booking), secure=True)

    assert first.status_code == 200
    assert first["Content-Type"] == "application/pdf"
    assert first.content.startswith(b"%PDF-")
    assert second.status_code == 200
    # Existing READY artifact is preferred; ensure_artifact should not re-run.
    assert generate_calls["count"] == 0

    assert (
        StaffActionAuditEvent.objects.filter(
            booking=booking,
            action=StaffActionAuditEvent.Action.RECEIPT_DOWNLOAD,
        ).count()
        == 2
    )
    assert (
        StaffSecurityAudit.objects.filter(
            event_type=StaffSecurityAudit.EventType.RECEIPT_DOWNLOAD,
        ).count()
        >= 2
    )

    payment = permitted.get(staff_payment_url(booking), secure=True)
    assert payment.status_code == 200
    assert payment.json()["receipt_status"] in {"paid", "issued"}


@pytest.mark.django_db(transaction=True)
def test_staff_receipt_pdf_uses_short_lived_cache_when_generating(settings, tmp_path, monkeypatch):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    cache.clear()
    booking, _session, _ledger = _confirm_paid_booking("staff-receipt-cache")

    # Drop any pre-created artifact so the staff path must generate once.
    if hasattr(booking.receipt, "pdf_artifact"):
        booking.receipt.pdf_artifact.delete()
    booking.receipt.pdf_status = BookingReceipt.PdfStatus.PENDING
    booking.receipt.pdf_storage_key = ""
    booking.receipt.save(update_fields=["pdf_status", "pdf_storage_key", "updated_at"])

    generate_calls = {"count": 0}
    original_ensure = ReceiptPDFService.ensure_artifact

    def counting_ensure(receipt):
        generate_calls["count"] += 1
        return original_ensure(receipt)

    monkeypatch.setattr(ReceiptPDFService, "ensure_artifact", staticmethod(counting_ensure))

    permitted = Client()
    staff_login(permitted, permissions=["view_staff_payment_summary"])
    first = permitted.get(staff_receipt_url(booking), secure=True)
    second = permitted.get(staff_receipt_url(booking), secure=True)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.content.startswith(b"%PDF-")
    # First request generates; second should hit short-lived cache or READY artifact.
    assert generate_calls["count"] == 1
