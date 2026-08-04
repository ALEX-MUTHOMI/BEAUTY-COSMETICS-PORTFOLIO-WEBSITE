from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession

User = get_user_model()


@pytest.mark.django_db
def test_direct_checkout_create_cannot_mass_assign_paid_or_provider_state():
    user = User.objects.create_user(email="payment-tamper@example.com", phone_number="+254700550001")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/checkout/sessions/",
        {
            "amount": "120.00",
            "currency": "KES",
            "description": "Payment tamper",
            "purchasable_type": "booking_candidate",
            "purchasable_id": "payment-tamper-target",
            "idempotency_key": "phase-3b-payment-tamper",
            "status": CheckoutSession.Status.PAID,
            "payment_status": "paid",
            "provider_status": "success",
            "provider_reference": "fake-provider-reference",
            "checkout_id": "fake-checkout-id",
            "ledger_id": "fake-ledger-id",
            "receipt_token": "fake-receipt-token",
            "is_paid": True,
        },
        format="json",
        secure=True,
    )

    assert response.status_code == 201
    session = CheckoutSession.objects.get(id=response.data["id"])
    assert session.status == CheckoutSession.Status.CREATED
    assert session.amount_snapshot == Decimal("120.00")
    assert LedgerTransaction.objects.count() == 0
    rendered = str(response.data)
    assert "fake-provider-reference" not in rendered
    assert "fake-ledger-id" not in rendered
    assert "fake-receipt-token" not in rendered


@pytest.mark.django_db
def test_disabled_billing_stk_endpoint_does_not_accept_client_payment_truth():
    response = APIClient().post(
        "/api/billing/stk-push/",
        {
            "email": "attacker@example.com",
            "amount": "1.00",
            "checkout_request_id": "attacker-checkout-request",
            "status": "success",
            "is_paid": True,
            "ledger_id": "attacker-ledger",
        },
        format="json",
        secure=True,
    )

    assert response.status_code == 410
    assert LedgerTransaction.objects.count() == 0
    rendered = str(response.data)
    assert "attacker-checkout-request" not in rendered
    assert "attacker-ledger" not in rendered
