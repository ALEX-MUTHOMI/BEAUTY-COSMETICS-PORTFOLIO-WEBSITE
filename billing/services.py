import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from billing.exceptions import BillingStateError
from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from billing.redaction import hash_sensitive_value, redact_financial_payload

logger = logging.getLogger(__name__)
User = get_user_model()


def _validate_amount(amount):
    if not isinstance(amount, Decimal):
        raise ValueError("Ledger amount must be a Decimal.")
    if amount <= Decimal("0.00"):
        raise ValueError("Ledger amount must be positive.")
    return amount.quantize(Decimal("0.01"))


def _create_audit_event(ledger, event_type, payload=None, correlation_id=None):
    redacted_payload = redact_financial_payload(payload or {})
    return FinancialAuditEvent.objects.create(
        ledger_transaction=ledger,
        event_type=event_type,
        source="system",
        redacted_payload=redacted_payload,
        payload_hash=hash_sensitive_value(redacted_payload),
        correlation_id=correlation_id,
    )


def create_pending_ledger_transaction(
    customer,
    amount,
    currency,
    direction,
    provider,
    provider_reference,
    external_correlation_id=None,
):
    amount = _validate_amount(amount)
    ledger = LedgerTransaction.objects.create(
        user=customer,
        amount=amount,
        currency=currency,
        direction=direction,
        provider=provider,
        provider_reference_hash=hash_sensitive_value(provider_reference),
        external_correlation_id=external_correlation_id,
    )
    _create_audit_event(
        ledger, "LEDGER_CREATED", {"provider_reference": provider_reference}
    )
    return ledger


def mark_ledger_success(
    ledger_id, provider_receipt, raw_payload=None, correlation_id=None
):
    with transaction.atomic():
        ledger = LedgerTransaction.objects.select_for_update().get(pk=ledger_id)
        if ledger.status != LedgerTransaction.Status.PENDING:
            raise BillingStateError(f"Cannot mark {ledger.status} ledger as success.")
        ledger.status = LedgerTransaction.Status.SUCCESS
        ledger.provider_receipt_hash = hash_sensitive_value(provider_receipt)
        ledger.mpesa_receipt_number = None
        ledger.credited_at = timezone.now()
        ledger.raw_payload = redact_financial_payload(raw_payload or {})
        ledger.save()
        _create_audit_event(ledger, "LEDGER_SUCCESS", raw_payload, correlation_id)
        SettlementRecord.objects.get_or_create(
            ledger_transaction=ledger,
            defaults={
                "amount": ledger.amount,
                "currency": ledger.currency,
                "settlement_status": SettlementRecord.Status.PENDING,
            },
        )
        return ledger


def mark_ledger_failed(ledger_id, reason, correlation_id=None):
    with transaction.atomic():
        ledger = LedgerTransaction.objects.select_for_update().get(pk=ledger_id)
        if ledger.status != LedgerTransaction.Status.PENDING:
            raise BillingStateError(f"Cannot mark {ledger.status} ledger as failed.")
        ledger.status = LedgerTransaction.Status.FAILED
        ledger.save()
        _create_audit_event(ledger, "LEDGER_FAILED", {"reason": reason}, correlation_id)
        return ledger


def record_reversal(ledger_id, reason, correlation_id=None):
    with transaction.atomic():
        ledger = LedgerTransaction.objects.select_for_update().get(pk=ledger_id)
        if ledger.status != LedgerTransaction.Status.SUCCESS:
            raise BillingStateError(
                "Only successful ledger transactions can be reversed."
            )
        ledger.status = LedgerTransaction.Status.REVERSED
        ledger.save()
        _create_audit_event(
            ledger, "LEDGER_REVERSED", {"reason": reason}, correlation_id
        )
        return ledger


def record_refund(ledger_id, reason, correlation_id=None):
    with transaction.atomic():
        ledger = LedgerTransaction.objects.select_for_update().get(pk=ledger_id)
        if ledger.status != LedgerTransaction.Status.SUCCESS:
            raise BillingStateError(
                "Only successful ledger transactions can be refunded."
            )
        ledger.status = LedgerTransaction.Status.REFUNDED
        ledger.save()
        _create_audit_event(
            ledger, "LEDGER_REFUNDED", {"reason": reason}, correlation_id
        )
        return ledger


def record_successful_checkout_payment(
    customer,
    checkout_session_id,
    amount,
    currency,
    provider_reference,
    provider_receipt,
    raw_payload=None,
    correlation_id=None,
):
    with transaction.atomic():
        ledger = (
            LedgerTransaction.objects.select_for_update()
            .filter(external_correlation_id=str(checkout_session_id))
            .first()
        )
        if ledger and ledger.status == LedgerTransaction.Status.SUCCESS:
            return ledger, False
        if ledger is None:
            ledger = create_pending_ledger_transaction(
                customer=customer,
                amount=amount,
                currency=currency,
                direction=LedgerTransaction.Direction.CREDIT,
                provider=LedgerTransaction.Provider.MPESA,
                provider_reference=provider_reference,
                external_correlation_id=str(checkout_session_id),
            )
        ledger = mark_ledger_success(
            ledger.id, provider_receipt, raw_payload, correlation_id
        )
        return ledger, True
