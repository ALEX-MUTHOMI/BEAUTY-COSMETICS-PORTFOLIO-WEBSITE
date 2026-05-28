import pytest

from checkout.models import MpesaWebhookInbox
from checkout.services import record_mpesa_webhook_event


@pytest.mark.django_db(transaction=True)
def test_webhook_inbox_event_hash_is_idempotent_for_replayed_payload():
    payload = {
        "CheckoutRequestID": "ws_CO_INBOX_REPLAY",
        "ResultCode": 0,
        "Amount": "100.00",
    }

    first = record_mpesa_webhook_event(payload, correlation_id="inbox-replay")
    duplicate = record_mpesa_webhook_event(payload, correlation_id="inbox-replay")

    assert first.processing_status == MpesaWebhookInbox.Status.RECEIVED
    assert duplicate.processing_status == MpesaWebhookInbox.Status.DUPLICATE
    assert MpesaWebhookInbox.objects.filter(event_hash=first.event_hash).count() == 1
