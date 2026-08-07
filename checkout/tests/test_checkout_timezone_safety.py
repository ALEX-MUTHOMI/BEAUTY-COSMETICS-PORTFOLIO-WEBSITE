from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_checkout_expiry_is_timezone_aware_utc():
    customer = User.objects.create_user(email="tz-checkout@aesthetic-os.test", phone_number="+254712700001")

    session = create_checkout_session(
        customer,
        Decimal("50.00"),
        "KES",
        "Timezone checkout",
        "booking_candidate",
        "tz-001",
        "tz-idem-001",
    )

    assert timezone.is_aware(session.created_at)
    assert timezone.is_aware(session.expires_at)
    assert session.expires_at > timezone.now()


@pytest.mark.django_db(transaction=True)
def test_callback_provider_timestamp_cannot_revive_expired_checkout_to_paid():
    """Late money is ledgered; checkout stays EXPIRED (no silent revive to PAID)."""
    customer = User.objects.create_user(email="tz-expired@aesthetic-os.test", phone_number="+254712700002")
    session = create_checkout_session(
        customer,
        Decimal("50.00"),
        "KES",
        "Expired timezone checkout",
        "booking_candidate",
        "tz-002",
        "tz-idem-002",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "tz-stk-002")
    CheckoutSession.objects.filter(pk=session.pk).update(
        status=CheckoutSession.Status.EXPIRED,
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "50.00",
            "MpesaReceiptNumber": "QTZ001",
            "ProviderTimestamp": "20991231235959",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.EXPIRED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_many_timezone_metadata_checkouts_keep_consistent_expiry():
    customer = User.objects.create_user(email="tz-storm@aesthetic-os.test", phone_number="+254712700003")
    zones = ["UTC", "Africa/Nairobi", "America/New_York", "Asia/Tokyo"]
    sessions = [
        create_checkout_session(
            customer,
            Decimal("10.00"),
            "KES",
            f"Timezone storm {zone}",
            "booking_candidate",
            f"tz-storm-{index}",
            f"tz-storm-idem-{index}",
        )
        for index, zone in enumerate(zones * 250)
    ]

    assert len(sessions) == 1000
    assert all(timezone.is_aware(session.expires_at) for session in sessions)
    assert len({session.status for session in sessions}) == 1
