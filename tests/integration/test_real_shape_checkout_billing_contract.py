import json
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.providers.mpesa import MpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk, process_mpesa_callback

User = get_user_model()
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "daraja"


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "fixture_name",
    ["stk_failure_callback.json", "stk_cancelled_callback.json", "stk_timeout_callback.json"],
)
def test_failed_cancelled_or_timeout_real_shape_callback_does_not_credit(fixture_name):
    customer = User.objects.create_user(email=f"{fixture_name}@beauty.com", phone_number="+254712770003")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Real shape failed",
        "booking_candidate",
        fixture_name,
        f"{fixture_name}-session",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, f"{fixture_name}-stk")
    event = MpesaProvider().normalize_callback(json.loads((FIXTURE_DIR / fixture_name).read_text()))
    attempt.provider_request_id = event["CheckoutRequestID"]
    attempt.merchant_request_id = event["MerchantRequestID"]
    attempt.save(update_fields=["provider_request_id", "merchant_request_id", "updated_at"])

    process_mpesa_callback(event, remote_addr="127.0.0.1")

    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 0
