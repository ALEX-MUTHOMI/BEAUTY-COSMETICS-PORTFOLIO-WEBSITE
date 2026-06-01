import time

import pytest

from bookings.models import Booking
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_pdf_generation_timeout_marks_artifact_failed_without_deconfirming(monkeypatch, settings):
    settings.RECEIPT_PDF_TIMEOUT_SECONDS = 0.01
    booking, _session, _ledger = _confirm_paid_booking("pdf-timeout")

    from bookings.models import ReceiptPDFArtifact
    from bookings.services import receipt_pdf
    from bookings.services.receipt_pdf import ReceiptPDFService

    def hanging_builder(lines):
        time.sleep(0.05)
        return b"%PDF-1.4\nslow\n%%EOF"

    monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", hanging_builder)

    with pytest.raises(TimeoutError):
        ReceiptPDFService.ensure_artifact(booking.receipt)

    booking.refresh_from_db()
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)
    assert booking.status == Booking.Status.CONFIRMED
    assert artifact.status == ReceiptPDFArtifact.Status.FAILED
    assert "timeout" in artifact.failure_reason_redacted.lower()
