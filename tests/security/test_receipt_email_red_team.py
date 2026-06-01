import pytest
from django.core.exceptions import ValidationError

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirmed(key):
    booking = _held_booking(key=key)
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"{key}-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="<script>raw-provider</script>",
        provider_receipt="RAW-RECEIPT",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    return booking


@pytest.mark.django_db(transaction=True)
def test_unpaid_failed_and_manual_review_bookings_have_no_normal_receipts_or_emails():
    unpaid = _held_booking(key="redteam-unpaid")
    _contract_service().create_checkout_for_held_booking(
        booking_public_id=unpaid.public_id,
        idempotency_key="redteam-unpaid-checkout",
    )
    failed = _held_booking(key="redteam-failed")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=failed.public_id,
        idempotency_key="redteam-failed-checkout",
    )
    _contract_service().fail_booking_after_payment_failure(
        checkout_session=CheckoutSession.objects.get(id=checkout["checkout_public_id"]),
        failure_reason="provider_failed",
    )

    assert BookingReceipt.objects.filter(booking__in=[unpaid, failed]).count() == 0
    assert BookingNotification.objects.filter(booking__in=[unpaid, failed]).count() == 0


@pytest.mark.django_db(transaction=True)
def test_email_pdf_and_download_surfaces_do_not_reflect_xss_or_provider_payload(caplog):
    booking = _confirmed("redteam-xss")
    booking.service.name = "<script>alert(1)</script>"
    booking.service.save(update_fields=["name", "updated_at"])

    from bookings.services.notification_delivery import build_notification_email
    from bookings.services.receipt_pdf import ReceiptPDFService
    from bookings.services.receipts import download_receipt_pdf_for_token

    notification = BookingNotification.objects.get(booking=booking, notification_type="booking_confirmed_with_receipt")
    email = build_notification_email(notification)
    pdf = ReceiptPDFService.generate_pdf(booking.receipt)
    token = booking.receipt.issue_download_token()
    downloaded = download_receipt_pdf_for_token(token)
    surface = f"{email.subject} {email.html} {email.text} {pdf!r} {downloaded!r} {caplog.text}"

    assert "<script" not in surface
    assert "raw-provider" not in surface
    assert "RAW-RECEIPT" not in surface
    assert "grace@example.com" not in surface
    assert "+254712345678" not in surface
    assert booking.receipt.checkout_session_id not in surface
    assert booking.receipt.billing_ledger_id not in surface


@pytest.mark.django_db(transaction=True)
def test_attacker_cannot_download_with_guessed_token_or_enumerate_receipt_number():
    booking = _confirmed("redteam-token")

    from bookings.services.receipts import download_receipt_pdf_for_token

    for token in ["", booking.receipt.receipt_number, str(booking.receipt.id), "A" * 64]:
        with pytest.raises(ValidationError):
            download_receipt_pdf_for_token(token)
