import pytest

from bookings.infrastructure.email_provider import EmailProviderError, _resolve_delivery_address
from bookings.models import BookingNotification
from bookings.services.notification_delivery import resolve_notification_recipient_email
from bookings.tests.test_b6_helpers import make_customer
from bookings.tests.test_booking_checkout_contract import _held_booking
from bookings.tests.test_notification_outbox_delivery import _confirmed_booking


@pytest.mark.django_db(transaction=True)
def test_resolve_notification_recipient_email_decrypts_customer_profile():
    booking = _confirmed_booking("notify-decrypt-recipient")
    notification = (
        BookingNotification.objects.filter(booking=booking).select_related("booking__customer_profile").first()
    )
    assert notification is not None
    email = resolve_notification_recipient_email(notification)
    assert email == "grace@example.com"


@pytest.mark.django_db
def test_resolve_notification_recipient_email_fail_closed_without_encrypted_email():
    booking = _held_booking(key="notify-decrypt-missing")
    profile = booking.customer_profile
    profile.email_encrypted = ""
    profile.save(update_fields=["email_encrypted", "updated_at"])
    notification = BookingNotification(
        booking=booking,
        recipient_email_hash="x",
        recipient_email_redacted="r***@example.com",
    )
    with pytest.raises(EmailProviderError, match="unavailable"):
        resolve_notification_recipient_email(notification)


def test_resolve_delivery_address_prefers_to_address_over_redacted(settings):
    settings.EMAIL_EXTERNAL_TEST_RECIPIENT = ""
    assert (
        _resolve_delivery_address(to_address="grace@example.com", to_redacted="g***@example.com") == "grace@example.com"
    )


def test_resolve_delivery_address_rejects_redacted_fallback(settings):
    settings.EMAIL_EXTERNAL_TEST_RECIPIENT = ""
    with pytest.raises(EmailProviderError):
        _resolve_delivery_address(to_address="", to_redacted="g***@example.com")


@pytest.mark.django_db
def test_make_customer_still_encrypts_email():
    profile = make_customer()
    assert "grace@example.com" not in profile.email_encrypted
