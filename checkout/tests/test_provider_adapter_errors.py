from decimal import Decimal

import pytest


def test_fake_mpesa_provider_can_simulate_timeout_and_outage_without_network():
    from checkout.providers.base import ProviderTimeout, ProviderUnavailable
    from checkout.providers.fake_mpesa import FakeMpesaProvider

    timeout_provider = FakeMpesaProvider(mode="timeout")
    outage_provider = FakeMpesaProvider(mode="outage")

    with pytest.raises(ProviderTimeout):
        timeout_provider.initiate_stk_push(
            phone_number="+254712600002",
            amount=Decimal("500.00"),
            account_reference="checkout-timeout",
            description="Timeout",
            callback_url="https://example.test/callback/",
            idempotency_key="timeout-idem",
        )

    with pytest.raises(ProviderUnavailable):
        outage_provider.initiate_stk_push(
            phone_number="+254712600003",
            amount=Decimal("500.00"),
            account_reference="checkout-outage",
            description="Outage",
            callback_url="https://example.test/callback/",
            idempotency_key="outage-idem",
        )
