import pytest

from checkout.models import MpesaWebhookInbox
from checkout.services import record_mpesa_webhook_event


@pytest.mark.django_db(transaction=True)
def test_webhook_inbox_idempotently_records_duplicate_event_as_duplicate():
    payload = {
        "CheckoutRequestID": "ws_CO_INBOX_001",
        "ResultCode": 0,
        "Amount": "100.00",
    }

    first = record_mpesa_webhook_event(payload, correlation_id="inbox-correlation")
    second = record_mpesa_webhook_event(payload, correlation_id="inbox-correlation")

    assert first.processing_status == MpesaWebhookInbox.Status.RECEIVED
    assert second.processing_status == MpesaWebhookInbox.Status.DUPLICATE
    assert MpesaWebhookInbox.objects.filter(event_hash=first.event_hash).count() == 1
    assert "ws_CO_INBOX_001" not in str(first.redacted_payload)
