import json
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from billing.models import LedgerTransaction
from checkout.exceptions import CheckoutValidationError
from checkout.models import CheckoutSession
from checkout.providers.mpesa import MpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk, process_mpesa_callback

User = get_user_model()
FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "daraja"


def _fixture(name):
    return json.loads((FIXTURE_DIR / name).read_text())


def _daraja_callback(checkout_request_id, result_code, amount=None):
    items = []
    if amount is not None:
        items.append({"Name": "Amount", "Value": float(amount)})
        items.append({"Name": "MpesaReceiptNumber", "Value": "QREDACTED001"})
    callback = {
        "MerchantRequestID": "merchant-redacted",
        "CheckoutRequestID": checkout_request_id,
        "ResultCode": result_code,
        "ResultDesc": "Provider result redacted",
    }
    if items:
        callback["CallbackMetadata"] = {"Item": items}
    return {"Body": {"stkCallback": callback}}


def _session_with_real_shape_attempt(status=CheckoutSession.Status.STK_SENT):
    customer = User.objects.create_user(email="real-shape-checkout@aesthetic-os.test", phone_number="+254712770001")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Real shape checkout",
        "booking_candidate",
        "real-shape-checkout",
        "real-shape-checkout-session",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "real-shape-checkout-stk")
    event = MpesaProvider().normalize_callback(_fixture("stk_success_callback.json"))
    attempt.provider_request_id = event["CheckoutRequestID"]
    attempt.merchant_request_id = event["MerchantRequestID"]
    attempt.save(update_fields=["provider_request_id", "merchant_request_id", "updated_at"])
    if status != CheckoutSession.Status.STK_SENT:
        CheckoutSession.objects.filter(pk=session.pk).update(status=status)
    return session, event


@pytest.mark.django_db(transaction=True)
def test_successful_daraja_shaped_callback_marks_checkout_paid_once():
    session, event = _session_with_real_shape_attempt()

    result = process_mpesa_callback(event, remote_addr="127.0.0.1")
    duplicate = process_mpesa_callback(event, remote_addr="127.0.0.1")
    session.refresh_from_db()

    assert result.session.status == CheckoutSession.Status.PAID
    assert duplicate.session is None
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 1


@pytest.mark.django_db(transaction=True)
def test_amount_mismatch_daraja_shaped_callback_does_not_pay():
    session, event = _session_with_real_shape_attempt()
    mismatch = MpesaProvider().normalize_callback(_fixture("amount_mismatch_callback.json"))

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(mismatch, remote_addr="127.0.0.1")

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.STK_SENT
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("terminal_status", [CheckoutSession.Status.EXPIRED, CheckoutSession.Status.CANCELLED])
def test_terminal_checkout_late_success_records_ledger_without_paid_transition(terminal_status):
    session, event = _session_with_real_shape_attempt(status=terminal_status)

    result = process_mpesa_callback(event, remote_addr="127.0.0.1")

    session.refresh_from_db()
    assert result.session is not None
    assert session.status == terminal_status
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_webhook_endpoint_accepts_nested_daraja_callback_shape():
    session, _ = _session_with_real_shape_attempt()
    client = APIClient()

    response = client.post(
        reverse("checkout-mpesa-webhook"),
        data=_fixture("stk_success_callback.json"),
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )
    session.refresh_from_db()

    assert response.status_code == 202
    assert session.status == CheckoutSession.Status.PAID
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        (_daraja_callback("ws_CO_UNKNOWN_SUCCESS", 0, "100.00"), 202),
        (_daraja_callback("ws_CO_UNKNOWN_CANCELLED", 1032), 202),
        (_daraja_callback("ws_CO_UNKNOWN_TIMEOUT", 1037), 202),
        (_daraja_callback("ws_CO_UNKNOWN_FAILED", 1), 202),
        ({"Body": {"stkCallback": {"CheckoutRequestID": "malformed-redacted"}}}, 400),
    ],
)
def test_webhook_endpoint_unknown_and_malformed_callbacks_fail_closed_without_ledger(payload, expected_status, caplog):
    client = APIClient()

    response = client.post(
        reverse("checkout-mpesa-webhook"),
        data=payload,
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )

    assert response.status_code == expected_status
    assert response.status_code < 500
    assert LedgerTransaction.objects.filter(status=LedgerTransaction.Status.SUCCESS).count() == 0
    assert CheckoutSession.objects.filter(status=CheckoutSession.Status.PAID).count() == 0
    assert "ws_CO_UNKNOWN" not in caplog.text
    assert "QREDACTED001" not in caplog.text


@pytest.mark.django_db(transaction=True)
def test_webhook_endpoint_amount_mismatch_callback_fails_closed_without_payment(caplog):
    session, event = _session_with_real_shape_attempt()
    payload = _daraja_callback(event["CheckoutRequestID"], 0, "999.00")
    client = APIClient()

    response = client.post(
        reverse("checkout-mpesa-webhook"),
        data=payload,
        format="json",
        REMOTE_ADDR="127.0.0.1",
        secure=True,
    )
    session.refresh_from_db()

    assert response.status_code == 202
    assert session.status == CheckoutSession.Status.STK_SENT
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 0
    assert event["CheckoutRequestID"] not in caplog.text
    assert "QREDACTED001" not in caplog.text
