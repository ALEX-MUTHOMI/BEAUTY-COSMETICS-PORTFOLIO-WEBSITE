from decimal import Decimal

from checkout.mpesa import build_stk_push_payload


def test_mpesa_payload_contract_uses_integer_amount_and_redactable_reference():
    payload = build_stk_push_payload(
        phone_number="+254712600004",
        amount=Decimal("750.00"),
        account_reference="checkout-payload-contract",
        description="Payload contract",
        callback_url="https://example.test/callback/",
    )

    assert payload["Amount"] == "750"
    assert payload["PhoneNumber"] == "254712600004"
    assert payload["AccountReference"] == "checkout-payload-contract"
