import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingNotification
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_email_provider_timeout_does_not_deconfirm_booking(settings, monkeypatch):
    settings.EMAIL_PROVIDER = "fake"
    booking = _held_booking(key="email-timeout-recovery")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="email-timeout-recovery-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-email-timeout",
        provider_receipt="receipt-email-timeout",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.services import notification_delivery
    from bookings.services.email_provider import EmailProviderError

    class TimeoutProvider:
        def send_email(self, **_kwargs):
            raise EmailProviderError("timeout")

    monkeypatch.setattr(notification_delivery, "get_email_provider", lambda: TimeoutProvider())
    result = notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10)

    booking.refresh_from_db()
    assert result.failed == 1
    assert booking.status == Booking.Status.CONFIRMED
    assert (
        BookingNotification.objects.filter(
            booking=booking,
            status=BookingNotification.Status.RETRY_SCHEDULED,
        ).count()
        == 1
    )
