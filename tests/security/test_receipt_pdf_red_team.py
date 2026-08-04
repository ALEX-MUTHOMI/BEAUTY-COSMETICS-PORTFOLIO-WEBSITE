import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_red_team_blocks_xss_lfi_remote_urls_and_provider_payloads():
    booking, _session, _ledger = _confirm_paid_booking("pdf-red-team")
    receipt = booking.receipt
    receipt.receipt_snapshot_json_redacted.update(
        {
            "service_name": '<script src="https://evil.test/x.js"></script>',
            "support_contact": "file:///etc/passwd ftp://evil.test/x http://evil.test/x",
            "policy_notice": "RAW-RECEIPT-123 CheckoutRequestID ws_CO_123 MerchantRequestID mr_123",
        }
    )
    receipt.save(update_fields=["receipt_snapshot_json_redacted", "updated_at"])

    from bookings.services.receipt_pdf import ReceiptPDFService

    pdf = ReceiptPDFService.generate_pdf(receipt)
    surface = pdf.decode("latin-1", "ignore")
    for forbidden in [
        "https://",
        "http://",
        "file://",
        "ftp://",
        "RAW-RECEIPT",
        "CheckoutRequestID",
        "MerchantRequestID",
    ]:
        assert forbidden not in surface
