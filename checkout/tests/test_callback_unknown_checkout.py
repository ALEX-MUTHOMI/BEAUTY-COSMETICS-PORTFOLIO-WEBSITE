import pytest

from checkout.exceptions import CheckoutValidationError
from checkout.models import MpesaWebhookInbox
from checkout.services import process_mpesa_callback


@pytest.mark.django_db(transaction=True)
def test_unknown_checkout_request_is_recorded_and_rejected_generically():
    with pytest.raises(CheckoutValidationError, match="could not be processed"):
        process_mpesa_callback(
            {
                "CheckoutRequestID": "ws_CO_UNKNOWN_A2",
                "MerchantRequestID": "merchant_unknown_a2",
                "ResultCode": 0,
                "Amount": "100.00",
                "MpesaReceiptNumber": "QUNKNOWN",
            },
            remote_addr="127.0.0.1",
        )

    inbox = MpesaWebhookInbox.objects.get()
    assert inbox.processing_status == MpesaWebhookInbox.Status.REJECTED
    assert "ws_CO_UNKNOWN_A2" not in str(inbox.redacted_payload)
