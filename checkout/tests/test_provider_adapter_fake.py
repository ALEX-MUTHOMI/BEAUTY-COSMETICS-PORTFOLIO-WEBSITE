from decimal import Decimal
from importlib.util import find_spec

import pytest


def test_fake_mpesa_provider_adapter_exists_for_default_tests():
    assert find_spec("checkout.providers.fake_mpesa") is not None


@pytest.mark.django_db
def test_fake_mpesa_provider_returns_deterministic_success_callback():
    from checkout.providers.fake_mpesa import FakeMpesaProvider

    provider = FakeMpesaProvider()
    response = provider.initiate_stk_push(
        phone_number="+254712600001",
        amount=Decimal("500.00"),
        account_reference="checkout-provider-001",
        description="Provider contract",
        callback_url="https://example.test/callback/",
        idempotency_key="provider-idem-001",
    )
    callback = provider.simulate_callback(response.checkout_request_id, success=True)

    assert response.checkout_request_id == "fake_ws_CO_provider-idem-001"
    assert response.merchant_request_id == "fake_merchant_provider-idem-001"
    assert callback["CheckoutRequestID"] == response.checkout_request_id
    assert callback["ResultCode"] == 0
