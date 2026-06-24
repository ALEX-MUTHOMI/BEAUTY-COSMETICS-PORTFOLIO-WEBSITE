import logging

from celery import shared_task

from billing.redaction import hash_sensitive_value, redact_financial_payload

logger = logging.getLogger(__name__)


@shared_task(name="billing.tasks.dlq_billing", queue="dlq_billing", ignore_result=True)
def dlq_billing(payload, reason, correlation_id=None):
    safe_payload = redact_financial_payload(payload)
    correlation_id_hash = hash_sensitive_value(correlation_id)[:16] if correlation_id else ""
    logger.critical(
        "Billing webhook payload routed to DLQ. reason=%s correlation_id_hash=%s payload=%s",
        reason,
        correlation_id_hash,
        safe_payload,
    )
    return True


@shared_task(
    bind=True,
    name="billing.tasks.process_mpesa_webhook",
    queue="billing",
    max_retries=3,
    default_retry_delay=1,
)
def process_mpesa_webhook(self, payload, correlation_id=None):
    reason = "Billing webhook processor is disabled; checkout owns M-Pesa callback orchestration."
    dlq_billing.apply_async(
        kwargs={
            "payload": redact_financial_payload(payload),
            "reason": reason,
            "correlation_id": correlation_id,
        },
        queue="dlq_billing",
    )
    correlation_id_hash = hash_sensitive_value(correlation_id)[:16] if correlation_id else ""
    logger.warning("%s correlation_id_hash=%s", reason, correlation_id_hash)
    return {"dlq": True, "reason": reason}
