from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from checkout.models import CheckoutSession
from checkout.services import create_checkout_session, expire_due_checkout_sessions

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_due_checkout_sessions_expire_without_touching_paid_sessions():
    customer = User.objects.create_user(email="expiry@aesthetic-os.test", phone_number="+254712200005")
    expired = create_checkout_session(
        customer,
        Decimal("300.00"),
        "KES",
        "Expired",
        "booking_candidate",
        "expiry-001",
        "expiry-idem-001",
    )
    paid = create_checkout_session(
        customer,
        Decimal("300.00"),
        "KES",
        "Paid",
        "booking_candidate",
        "expiry-002",
        "expiry-idem-002",
    )
    CheckoutSession.objects.filter(pk=expired.pk).update(
        expires_at=timezone.now(),
        status=CheckoutSession.Status.STK_SENT,
    )
    CheckoutSession.objects.filter(pk=paid.pk).update(expires_at=timezone.now(), status=CheckoutSession.Status.PAID)

    assert expire_due_checkout_sessions() == 1
    expired.refresh_from_db()
    paid.refresh_from_db()
    assert expired.status == CheckoutSession.Status.EXPIRED
    assert paid.status == CheckoutSession.Status.PAID
