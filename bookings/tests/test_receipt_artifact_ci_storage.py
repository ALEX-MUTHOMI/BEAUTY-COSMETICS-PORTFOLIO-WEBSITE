import os

import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_artifact_uses_ci_writable_configured_storage(settings, tmp_path):
    from bookings.models import ReceiptPDFArtifact
    from bookings.services.receipt_pdf import ReceiptPDFService

    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("ci-storage")

    pdf = ReceiptPDFService.ensure_artifact(booking.receipt)
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)
    artifact_path = tmp_path / os.path.basename(artifact.storage_key)

    assert pdf.startswith(b"%PDF-")
    assert artifact_path.exists()
    assert str(artifact_path).startswith(str(tmp_path))
    assert artifact.status == ReceiptPDFArtifact.Status.READY
    assert artifact.size_bytes == artifact_path.stat().st_size
