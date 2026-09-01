import os

import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


def test_receipt_pdf_artifact_default_storage_is_writable_runtime_path(settings):
    path = getattr(settings, "RECEIPT_PDF_ARTIFACT_DIR", "")
    normalized = str(path).replace("\\", "/")

    assert normalized
    assert normalized == "/app/var/receipt-artifacts"
    assert "/app/.local" not in normalized


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_artifact_uses_ci_writable_configured_storage(settings, tmp_path):
    from bookings.models import ReceiptPDFArtifact
    from bookings.services.receipt_pdf import ReceiptPDFService

    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("ci-storage")

    pdf = ReceiptPDFService.ensure_artifact(booking.receipt)
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)
    artifact_path = tmp_path / os.path.basename(artifact.storage_key)

    assert pdf.startswith(b"%PDF-")
    assert artifact_path.exists()
    assert not artifact_path.read_bytes().startswith(b"%PDF-")
    assert ReceiptPDFService.read_artifact(artifact).startswith(b"%PDF-")
    assert str(artifact_path).startswith(str(tmp_path))
    assert artifact.status == ReceiptPDFArtifact.Status.READY
    assert artifact.size_bytes == len(pdf)
