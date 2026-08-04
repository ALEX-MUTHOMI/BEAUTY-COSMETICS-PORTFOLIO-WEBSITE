import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_pdf_renderer_rejects_remote_and_local_resource_references():
    booking, _session, _ledger = _confirm_paid_booking("pdf-resource-red-team")
    receipt = booking.receipt
    receipt.receipt_snapshot_json_redacted["service_name"] = (
        '<img src="https://attacker.test/pixel.png">'
        '<link href="http://attacker.test/font.css">'
        '<img src="file:///etc/passwd">'
        '<img src="ftp://attacker.test/x">'
        "<script>alert(1)</script>"
        "C:\\Windows\\win.ini"
    )
    receipt.save(update_fields=["receipt_snapshot_json_redacted", "updated_at"])

    from bookings.services.receipt_pdf import ReceiptPDFService

    pdf = ReceiptPDFService.generate_pdf(receipt)
    surface = pdf.decode("latin-1", "ignore")
    assert "https://" not in surface
    assert "http://" not in surface
    assert "file://" not in surface
    assert "ftp://" not in surface
    assert "script" not in surface.lower()
    assert "win.ini" not in surface


@pytest.mark.django_db(transaction=True)
def test_pdf_uses_immutable_snapshot_not_live_service_mutation():
    booking, _session, _ledger = _confirm_paid_booking("pdf-snapshot")
    original_service_name = booking.receipt.receipt_snapshot_json_redacted["service_name"]
    booking.service.name = "MUTATED LIVE SERVICE NAME"
    booking.service.base_price = "999999.00"
    booking.service.save(update_fields=["name", "base_price", "updated_at"])

    from bookings.services.receipt_pdf import ReceiptPDFService

    pdf = ReceiptPDFService.generate_pdf(booking.receipt)
    assert original_service_name.encode() in pdf
    assert b"MUTATED LIVE SERVICE NAME" not in pdf
    assert b"999999.00" not in pdf
