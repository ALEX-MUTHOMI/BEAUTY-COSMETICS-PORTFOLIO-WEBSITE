import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_booking_checkout_billing_receipt_email_contract(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = _held_booking(key="receipt-email-contract")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="receipt-email-contract-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-contract",
        provider_receipt="receipt-contract",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.services.notification_delivery import BookingNotificationDeliveryService
    from bookings.services.receipts import download_receipt_pdf_for_token

    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert BookingNotification.objects.filter(booking=booking).count() == 2
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 2
    token = booking.receipt.issue_download_token()
    assert download_receipt_pdf_for_token(token).startswith(b"%PDF-")
