from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from billing.models import LedgerTransaction
from checkout.providers.base import ProviderTimeout
from checkout.services import create_checkout_session

User = get_user_model()


class TimeoutProvider:
    def initiate_stk_push(self, *args, **kwargs):
        raise ProviderTimeout("raw timeout should not leak")


@pytest.mark.django_db(transaction=True)
def test_provider_timeout_returns_controlled_response_without_credit(monkeypatch):
    customer = User.objects.create_user(
        email="provider-timeout@beauty.com", phone_number="+254712730002"
    )
    session = create_checkout_session(
        customer,
        Decimal("130.00"),
        "KES",
        "Provider timeout",
        "booking_candidate",
        "provider-timeout",
        "provider-timeout-session",
    )
    monkeypatch.setattr(
        "checkout.services.get_mpesa_provider", lambda: TimeoutProvider()
    )

    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    client.force_authenticate(user=customer)
    response = client.post(
        f"/api/checkout/sessions/{session.id}/mpesa/stk/",
        {
            "phone_number": customer.phone_number,
            "idempotency_key": "provider-timeout-stk",
        },
        format="json",
        REMOTE_ADDR="198.51.100.10",
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.data == {"detail": "Payment provider temporarily unavailable."}
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 0
    )
