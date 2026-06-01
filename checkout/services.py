import logging
from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.redaction import hash_sensitive_value, redact_phone
from billing.services import record_successful_checkout_payment
from checkout.exceptions import CheckoutStateError, CheckoutValidationError
from checkout.models import CheckoutAttempt, CheckoutSession, MpesaWebhookInbox
from checkout.mpesa import normalize_mpesa_phone
from checkout.providers import FakeMpesaProvider, MpesaProvider
from checkout.redaction import redact_checkout_payload
from checkout.state_machine import transition_checkout

logger = logging.getLogger(__name__)


@dataclass
class CallbackResult:
    session: CheckoutSession | None
    inbox: MpesaWebhookInbox


def _validate_amount(amount):
    if not isinstance(amount, Decimal):
        raise ValueError("Checkout amount must be a Decimal.")
    if amount <= Decimal("0.00"):
        raise ValueError("Checkout amount must be positive.")
    return amount.quantize(Decimal("0.01"))


def create_checkout_session(
    customer,
    amount,
    currency,
    description,
    purchasable_type,
    purchasable_id,
    idempotency_key,
):
    amount = _validate_amount(amount)
    if not idempotency_key:
        raise ValueError("idempotency key is required.")
    session, _ = CheckoutSession.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "customer": customer,
            "amount_snapshot": amount,
            "currency": currency,
            "description_snapshot": description,
            "purchasable_type": purchasable_type,
            "purchasable_id": purchasable_id,
            "expires_at": timezone.now() + timezone.timedelta(minutes=15),
        },
    )
    return session


def get_mpesa_provider():
    provider_mode = getattr(
        settings,
        "PAYMENT_PROVIDER_MODE",
        getattr(settings, "CHECKOUT_MPESA_PROVIDER", "fake"),
    )
    if provider_mode in {"real", "daraja_sandbox", "daraja_live"}:
        return MpesaProvider()
    return FakeMpesaProvider()


def initiate_mpesa_stk(session_id, phone_number, idempotency_key, provider=None):
    normalized_phone = normalize_mpesa_phone(phone_number)
    provider = provider or get_mpesa_provider()
    with transaction.atomic():
        session = CheckoutSession.objects.select_for_update().get(pk=session_id)
        if session.status in {
            CheckoutSession.Status.PAID,
            CheckoutSession.Status.FAILED,
            CheckoutSession.Status.EXPIRED,
            CheckoutSession.Status.CANCELLED,
        }:
            raise CheckoutStateError("Cannot initiate STK for a terminal checkout.")
        existing = CheckoutAttempt.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing
        if session.status == CheckoutSession.Status.CREATED:
            transition_checkout(session, CheckoutSession.Status.PAYMENT_PENDING)
        provider_response = provider.initiate_stk_push(
            phone_number=normalized_phone,
            amount=session.amount_snapshot,
            account_reference=str(session.id),
            description=session.description_snapshot,
            callback_url=settings.DARAJA_CALLBACK_URL,
            idempotency_key=idempotency_key,
        )
        attempt = CheckoutAttempt.objects.create(
            checkout_session=session,
            phone_number_hash=hash_sensitive_value(normalized_phone),
            redacted_phone=redact_phone(normalized_phone),
            provider_request_id=provider_response.checkout_request_id,
            merchant_request_id=provider_response.merchant_request_id,
            idempotency_key=idempotency_key,
            status=CheckoutAttempt.Status.SENT,
            raw_request_hash=hash_sensitive_value(provider_response),
            redacted_request_payload=redact_checkout_payload(
                {
                    "CheckoutRequestID": provider_response.checkout_request_id,
                    "MerchantRequestID": provider_response.merchant_request_id,
                    "PhoneNumber": normalized_phone,
                }
            ),
        )
        if session.status != CheckoutSession.Status.STK_SENT:
            transition_checkout(session, CheckoutSession.Status.STK_SENT)
        return attempt


def _event_hash(payload):
    return hash_sensitive_value(payload)


def _checkout_request_id(payload):
    return str(payload.get("CheckoutRequestID") or payload.get("checkout_request_id") or "")


def record_mpesa_webhook_event(payload, correlation_id=None):
    checkout_request_id = _checkout_request_id(payload)
    event_hash = _event_hash(payload)
    event, created = MpesaWebhookInbox.objects.get_or_create(
        event_hash=event_hash,
        defaults={
            "checkout_request_id_hash": (hash_sensitive_value(checkout_request_id) if checkout_request_id else ""),
            "redacted_payload": redact_checkout_payload(payload),
            "correlation_id": correlation_id,
        },
    )
    if created:
        return event
    event.processing_status = MpesaWebhookInbox.Status.DUPLICATE
    return event


def mark_webhook_event_status(inbox_id, status, processed=True):
    updates = {"processing_status": status}
    if processed:
        updates["processed_at"] = timezone.now()
    MpesaWebhookInbox.objects.filter(pk=inbox_id).update(**updates)


def expire_checkout_session(session_id):
    with transaction.atomic():
        session = CheckoutSession.objects.select_for_update().get(pk=session_id)
        return transition_checkout(session, CheckoutSession.Status.EXPIRED)


def cancel_checkout_session(session_id):
    with transaction.atomic():
        session = CheckoutSession.objects.select_for_update().get(pk=session_id)
        return transition_checkout(session, CheckoutSession.Status.CANCELLED)


def expire_due_checkout_sessions():
    count = 0
    for session in CheckoutSession.objects.filter(
        expires_at__lte=timezone.now(),
        status__in=[
            CheckoutSession.Status.CREATED,
            CheckoutSession.Status.PAYMENT_PENDING,
            CheckoutSession.Status.STK_SENT,
        ],
    ):
        expire_checkout_session(session.id)
        count += 1
    return count


def process_mpesa_callback(payload, remote_addr=None, correlation_id=None):
    checkout_request_id = _checkout_request_id(payload)
    if not checkout_request_id:
        raise CheckoutValidationError("Malformed provider callback.")

    inbox = record_mpesa_webhook_event(payload, correlation_id)
    if inbox.processing_status == MpesaWebhookInbox.Status.DUPLICATE:
        return CallbackResult(session=None, inbox=inbox)

    try:
        with transaction.atomic():
            inbox = MpesaWebhookInbox.objects.select_for_update().get(pk=inbox.pk)
            return _process_locked_callback(payload, checkout_request_id, inbox, correlation_id)
    except (CheckoutValidationError, CheckoutStateError):
        mark_webhook_event_status(inbox.id, MpesaWebhookInbox.Status.REJECTED)
        raise
    except Exception:
        mark_webhook_event_status(inbox.id, MpesaWebhookInbox.Status.FAILED)
        raise


def _process_locked_callback(payload, checkout_request_id, inbox, correlation_id=None):
    attempt = (
        CheckoutAttempt.objects.select_for_update()
        .select_related("checkout_session", "checkout_session__customer")
        .filter(provider_request_id=checkout_request_id)
        .first()
    )
    if attempt is None:
        raise CheckoutValidationError("Provider callback could not be processed.")

    session = CheckoutSession.objects.select_for_update().get(pk=attempt.checkout_session_id)
    result_code = int(payload.get("ResultCode", payload.get("result_code", 1)))
    if session.status == CheckoutSession.Status.PAID and result_code != 0:
        inbox.processing_status = MpesaWebhookInbox.Status.DUPLICATE
        inbox.processed_at = timezone.now()
        inbox.save(update_fields=["processing_status", "processed_at", "updated_at"])
        return CallbackResult(session=session, inbox=inbox)
    if session.status in {
        CheckoutSession.Status.EXPIRED,
        CheckoutSession.Status.CANCELLED,
    }:
        raise CheckoutStateError("Terminal checkout cannot be paid.")

    raw_amount = payload.get("Amount", payload.get("amount"))
    if result_code == 0:
        amount = Decimal(str(raw_amount or "0.00")).quantize(Decimal("0.01"))
        if amount != session.amount_snapshot:
            raise CheckoutValidationError("Provider callback amount mismatch.")

    attempt.status = CheckoutAttempt.Status.CALLBACK_RECEIVED
    attempt.save(update_fields=["status", "updated_at"])

    if result_code == 0:
        transition_checkout(session, CheckoutSession.Status.PAID)
        attempt.status = CheckoutAttempt.Status.SUCCESS
        attempt.save(update_fields=["status", "updated_at"])
        record_successful_checkout_payment(
            customer=session.customer,
            checkout_session_id=session.id,
            amount=session.amount_snapshot,
            currency=session.currency,
            provider_reference=attempt.provider_request_id,
            provider_receipt=str(payload.get("MpesaReceiptNumber", "")),
            raw_payload=payload,
            correlation_id=correlation_id,
        )
        if session.purchasable_type == "booking":
            from bookings.services.checkout_contract import BookingCheckoutContractService

            ledger = LedgerTransaction.objects.get(external_correlation_id=str(session.id))
            BookingCheckoutContractService.confirm_booking_after_billing_success(
                checkout_session=session,
                billing_ledger=ledger,
                request_context={"request_id": correlation_id},
            )
    else:
        transition_checkout(session, CheckoutSession.Status.FAILED)
        attempt.status = CheckoutAttempt.Status.FAILED
        attempt.save(update_fields=["status", "updated_at"])
        if session.purchasable_type == "booking":
            from bookings.services.checkout_contract import BookingCheckoutContractService

            BookingCheckoutContractService.fail_booking_after_payment_failure(
                checkout_session=session,
                failure_reason=str(result_code),
                request_context={"request_id": correlation_id},
            )

    inbox.processing_status = MpesaWebhookInbox.Status.PROCESSED
    inbox.processed_at = timezone.now()
    inbox.save(update_fields=["processing_status", "processed_at", "updated_at"])
    return CallbackResult(session=session, inbox=inbox)
