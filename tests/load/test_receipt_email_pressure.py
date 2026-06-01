import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_duplicate_receipt_email_pressure_is_bounded(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = _held_booking(key="receipt-email-pressure")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="receipt-email-pressure-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-pressure",
        provider_receipt="receipt-pressure",
    )
    for _index in range(100):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert BookingNotification.objects.filter(booking=booking).count() == 1
    assert BookingNotificationDeliveryService.send_pending(limit=100).sent == 1
