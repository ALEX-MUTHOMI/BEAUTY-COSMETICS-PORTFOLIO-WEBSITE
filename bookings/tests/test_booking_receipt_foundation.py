import pytest
from django.utils import timezone

from billing.services import record_successful_checkout_payment
from bookings.models import Booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirm_paid_booking(key):
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
        provider_reference=f"provider-{key}",
        provider_receipt=f"receipt-{key}",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    return booking, session, ledger


@pytest.mark.django_db(transaction=True)
def test_receipt_and_email_outbox_created_only_after_confirmed_paid_booking():
    booking, session, ledger = _confirm_paid_booking("receipt-foundation")

    from bookings.models import BookingNotification, BookingReceipt

    receipt = BookingReceipt.objects.get(booking=booking)
    notification = BookingNotification.objects.get(booking=booking)
    assert receipt.checkout_session_id == str(session.id)
    assert receipt.billing_ledger_id == str(ledger.id)
    assert receipt.amount == session.amount_snapshot
    assert receipt.currency == "KES"
    assert receipt.payment_status == "paid"
    assert receipt.booking_status == Booking.Status.CONFIRMED
    assert receipt.download_token_hash
    assert receipt.download_token_expires_at > timezone.now()
    assert "receipt-" not in str(receipt.receipt_snapshot_json_redacted)
    assert "+254712345678" not in str(receipt.receipt_snapshot_json_redacted)
    assert "***" in receipt.receipt_snapshot_json_redacted["redacted_phone"]
    assert notification.notification_type == "booking_confirmed"
    assert notification.status == "pending"


@pytest.mark.django_db(transaction=True)
def test_duplicate_confirmation_creates_one_receipt_and_one_email_outbox():
    booking, session, ledger = _confirm_paid_booking("receipt-duplicate")
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.models import BookingNotification, BookingReceipt

    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert BookingNotification.objects.filter(booking=booking, notification_type="booking_confirmed").count() == 1


@pytest.mark.django_db(transaction=True)
def test_no_receipt_for_payment_pending_failed_or_manual_review():
    pending = _held_booking(key="receipt-pending")
    _contract_service().create_checkout_for_held_booking(
        booking_public_id=pending.public_id,
        idempotency_key="receipt-pending-checkout",
    )

    failed = _held_booking(key="receipt-failed")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=failed.public_id,
        idempotency_key="receipt-failed-checkout",
    )
    _contract_service().fail_booking_after_payment_failure(
        checkout_session=CheckoutSession.objects.get(id=checkout["checkout_public_id"]),
        failure_reason="provider_failed",
    )

    from bookings.models import BookingReceipt

    assert BookingReceipt.objects.filter(booking__in=[pending, failed]).count() == 0
