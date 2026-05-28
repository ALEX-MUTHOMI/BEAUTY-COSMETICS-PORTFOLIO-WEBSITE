import json
from pathlib import Path

import pytest

from checkout.exceptions import CheckoutValidationError
from checkout.providers.mpesa import MpesaProvider

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "daraja"


def _fixture(name):
    return json.loads((FIXTURE_DIR / name).read_text())


@pytest.mark.parametrize(
    ("fixture_name", "expected_code"),
    [
        ("stk_success_callback.json", 0),
        ("stk_failure_callback.json", 1032),
        ("stk_timeout_or_cancelled_callback.json", 1037),
    ],
)
def test_daraja_real_shaped_callbacks_normalize_to_internal_contract(
    fixture_name, expected_code
):
    event = MpesaProvider().normalize_callback(_fixture(fixture_name))

    assert event["CheckoutRequestID"] == "ws_CO_SANITIZED_12345"
    assert event["MerchantRequestID"] == "merchant_SANITIZED_12345"
    assert event["ResultCode"] == expected_code
    assert "Amount" in event


def test_malformed_daraja_callback_rejected_safely():
    with pytest.raises(CheckoutValidationError):
        MpesaProvider().normalize_callback(_fixture("malformed_callback.json"))


def test_amount_mismatch_fixture_retains_provider_amount_for_state_machine_rejection():
    event = MpesaProvider().normalize_callback(
        _fixture("amount_mismatch_callback.json")
    )

    assert event["CheckoutRequestID"] == "ws_CO_SANITIZED_12345"
    assert event["Amount"] == "9999.00"
