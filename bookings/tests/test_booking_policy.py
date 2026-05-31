from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from bookings.models import Booking, BookingFinancialHistory, BookingRescheduleRequest
from bookings.services.rescheduling import create_reschedule_request
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_no_refund_policy_acceptance_and_financial_history_snapshot():
    booking = create_booking(status=Booking.Status.CONFIRMED)
    booking.no_refund_policy_accepted_at = timezone.now()
    booking.save()

    history = BookingFinancialHistory.objects.create(
        booking=booking,
        checkout_session_id="checkout-redacted",
        billing_ledger_id="ledger-redacted",
        event_type=BookingFinancialHistory.EventType.PAYMENT_CONFIRMED,
        amount=Decimal("2500.00"),
        currency="KES",
        provider_reference_hash="hash-only",
        no_refund_policy_version="v1",
    )

    assert history.billing_ledger_id == "ledger-redacted"
    assert booking.no_refund_policy_accepted_at is not None
    assert not hasattr(booking, "refund")


@pytest.mark.django_db
def test_reschedule_request_links_original_billing_without_zero_ledger():
    booking = create_booking(status=Booking.Status.CONFIRMED, reschedule_count=0)

    request = create_reschedule_request(
        booking,
        requested_starts_at=booking.starts_at + timedelta(days=1),
        requested_ends_at=booking.ends_at + timedelta(days=1),
        reason="customer requested a safer time",
        original_billing_ledger_id="ledger-existing",
    )

    assert request.status == BookingRescheduleRequest.Status.REQUESTED
    assert request.original_billing_ledger_id == "ledger-existing"
    assert request.additional_fee_amount == Decimal("0.00")
    assert request.new_checkout_session_id == ""
