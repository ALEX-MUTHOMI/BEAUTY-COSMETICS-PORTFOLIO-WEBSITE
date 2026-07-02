from decimal import Decimal

import pytest

from checkout.exceptions import CheckoutValidationError
from checkout.mpesa import build_stk_push_payload, normalize_mpesa_phone


def test_create_stk_push_payload_with_normalized_kenyan_msisdn():
    payload = build_stk_push_payload(
        phone_number="0712200003",
        amount=Decimal("1999.00"),
        account_reference="checkout-001",
        description="AestheticOS checkout",
        callback_url="https://example.test/mpesa/",
    )

    assert payload["PhoneNumber"] == "254712200003"
    assert payload["PartyA"] == "254712200003"
    assert payload["Amount"] == "1999"
    assert payload["AccountReference"] == "checkout-001"


def test_invalid_mpesa_phone_rejected():
    with pytest.raises(CheckoutValidationError):
        normalize_mpesa_phone("+15551234567")
