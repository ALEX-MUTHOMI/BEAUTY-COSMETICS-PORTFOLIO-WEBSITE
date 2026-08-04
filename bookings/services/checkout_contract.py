import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.redaction import hash_sensitive_value
from bookings.models import (
    Booking,
    BookingAuditEvent,
    BookingFinancialHistory,
    BookingPriceSnapshot,
)
from bookings.privacy import decrypt_value
from bookings.services.legal import (
    assert_checkout_policy_accepted,
    has_policy_acceptance,
    record_booking_policy_acceptance,
)
from bookings.services.state_machine import BookingStateError, transition_booking
from checkout.models import CheckoutSession
from checkout.services import create_checkout_session
from checkout.state_machine import transition_checkout

logger = logging.getLogger("bookings.checkout_contract")
User = get_user_model()

GENERIC_PAYMENT_ERROR = "Unable to process booking payment request."
GENERIC_CHECKOUT_UNAVAILABLE = "Booking is not available for checkout."
CHECKOUT_COUNTER_TTL_SECONDS = 600


def _safe_counter(redis_client, key):
    if not redis_client:
        return
    try:
        redis_client.incr(key)
        redis_client.expire(key, CHECKOUT_COUNTER_TTL_SECONDS)
    except Exception:
        logger.info("booking.checkout.redis_degraded", extra={"counter_key": key})


def _booking_amount(booking):
    if booking.total_price_snapshot and booking.total_price_snapshot > Decimal("0.00"):
        return {
            "base_service_price": booking.total_price_snapshot.quantize(Decimal("0.01")),
            "urgent_fee": Decimal("0.00"),
            "sunday_surcharge": Decimal("0.00"),
            "total_amount": booking.total_price_snapshot.quantize(Decimal("0.01")),
            "currency": booking.currency_snapshot or "KES",
        }
    base = booking.service.base_price
    urgent_fee = booking.service.urgent_fee if booking.booking_type == Booking.BookingType.URGENT else Decimal("0.00")
    sunday_fee = (
        booking.service.sunday_surcharge
        if booking.booking_type == Booking.BookingType.SUNDAY_URGENT
        else Decimal("0.00")
    )
    return {
        "base_service_price": base.quantize(Decimal("0.01")),
        "urgent_fee": urgent_fee.quantize(Decimal("0.01")),
        "sunday_surcharge": sunday_fee.quantize(Decimal("0.01")),
        "total_amount": (base + urgent_fee + sunday_fee).quantize(Decimal("0.01")),
        "currency": "KES",
    }


def _price_snapshot(booking):
    amounts = _booking_amount(booking)
    snapshot, _created = BookingPriceSnapshot.objects.get_or_create(
        booking=booking,
        defaults=amounts,
    )
    return snapshot


def _checkout_customer(booking):
    email = decrypt_value(booking.customer_profile.email_encrypted)
    phone = decrypt_value(booking.customer_profile.phone_encrypted)
    user = User.objects.filter(email=email).first()
    if user is None:
        try:
            with transaction.atomic():
                user = User.objects.create_user(email=email, phone_number=phone)
        except IntegrityError:
            user = User.objects.filter(email=email).first()
            if user is None:
                raise ValidationError(GENERIC_PAYMENT_ERROR)
    return user


def _history_exists(booking, event_type, checkout_session_id="", billing_ledger_id=""):
    queryset = BookingFinancialHistory.objects.filter(booking=booking, event_type=event_type)
    if checkout_session_id:
        queryset = queryset.filter(checkout_session_id=str(checkout_session_id))
    if billing_ledger_id:
        queryset = queryset.filter(billing_ledger_id=str(billing_ledger_id))
    return queryset.exists()


def _create_history(booking, event_type, amount, currency, checkout_session_id="", billing_ledger_id=""):
    if _history_exists(booking, event_type, checkout_session_id, billing_ledger_id):
        return None
    return BookingFinancialHistory.objects.create(
        booking=booking,
        checkout_session_id=str(checkout_session_id) if checkout_session_id else "",
        billing_ledger_id=str(billing_ledger_id) if billing_ledger_id else "",
        event_type=event_type,
        amount=amount,
        currency=currency,
        provider_reference_hash="",
        no_refund_policy_version=booking.terms_version,
    )


def _safe_response(booking, checkout_session, next_action="initiate_payment"):
    return {
        "booking_public_id": str(booking.public_id),
        "status_url": f"/booking/status/{booking.public_id}/",
        "status_api_url": f"/api/bookings/status/{booking.public_id}/",
        "checkout_public_id": str(checkout_session.id),
        "booking_status": booking.status,
        "payment_status": checkout_session.status,
        "amount": f"{checkout_session.amount_snapshot:.2f}",
        "currency": checkout_session.currency,
        "next_action": next_action,
    }


def _is_matching_checkout(session, booking, snapshot):
    return (
        session.purchasable_type == "booking"
        and session.purchasable_id == str(booking.id)
        and session.amount_snapshot == snapshot.total_amount
        and session.currency == snapshot.currency
    )


class BookingCheckoutContractService:
    @classmethod
    def create_checkout_for_held_booking(cls, *, booking_public_id, idempotency_key, request_context=None):
        request_context = request_context or {}
        redis_client = request_context.get("redis_client")
        _safe_counter(redis_client, "booking:checkout:attempted:10m")

        try:
            with transaction.atomic():
                booking = (
                    Booking.objects.select_for_update(of=("self",))
                    .select_related("customer_profile", "service")
                    .get(public_id=booking_public_id)
                )
                snapshot = _price_snapshot(booking)

                existing = CheckoutSession.objects.select_for_update().filter(idempotency_key=idempotency_key).first()
                if existing:
                    if not _is_matching_checkout(existing, booking, snapshot):
                        _safe_counter(redis_client, "booking:checkout:rejected:10m")
                        raise ValidationError(GENERIC_PAYMENT_ERROR)
                    if booking.status not in {Booking.Status.HELD, Booking.Status.PAYMENT_PENDING}:
                        _safe_counter(redis_client, "booking:checkout:rejected:10m")
                        raise ValidationError(GENERIC_CHECKOUT_UNAVAILABLE)
                    if not has_policy_acceptance(booking=booking, checkout_session=existing):
                        documents = assert_checkout_policy_accepted(request_context.get("policy_acceptance"))
                        record_booking_policy_acceptance(
                            booking=booking,
                            checkout_session=existing,
                            documents=documents,
                            policy_acceptance=request_context.get("policy_acceptance"),
                            request_context=request_context,
                        )
                    cls._mark_payment_pending_if_needed(booking, existing, request_context)
                    _safe_counter(redis_client, "booking:checkout:replayed:10m")
                    return _safe_response(booking, existing)

                cls._validate_checkout_eligible(booking)
                documents = assert_checkout_policy_accepted(request_context.get("policy_acceptance"))
                customer = _checkout_customer(booking)
                try:
                    session = create_checkout_session(
                        customer=customer,
                        amount=snapshot.total_amount,
                        currency=snapshot.currency,
                        description=f"Booking {booking.public_id}",
                        purchasable_type="booking",
                        purchasable_id=str(booking.id),
                        idempotency_key=idempotency_key,
                    )
                except IntegrityError:
                    session = CheckoutSession.objects.select_for_update().get(idempotency_key=idempotency_key)
                    if not _is_matching_checkout(session, booking, snapshot):
                        raise ValidationError(GENERIC_PAYMENT_ERROR)

                record_booking_policy_acceptance(
                    booking=booking,
                    checkout_session=session,
                    documents=documents,
                    policy_acceptance=request_context.get("policy_acceptance"),
                    request_context=request_context,
                )
                cls._mark_payment_pending_if_needed(booking, session, request_context)
                _safe_counter(redis_client, "booking:checkout:created:10m")
                _safe_counter(redis_client, f"booking:checkout:booking:{booking.public_id}:10m")
                logger.info(
                    "booking.checkout.created",
                    extra={
                        "booking_public_id": str(booking.public_id),
                        "checkout_public_hash": hash_sensitive_value(str(session.id))[:16],
                        "request_id": request_context.get("request_id"),
                    },
                )
                return _safe_response(booking, session)
        except Booking.DoesNotExist as exc:
            _safe_counter(redis_client, "booking:checkout:rejected:10m")
            raise ValidationError(GENERIC_CHECKOUT_UNAVAILABLE) from exc

    @staticmethod
    def _validate_checkout_eligible(booking):
        if booking.status != Booking.Status.HELD:
            raise ValidationError(GENERIC_CHECKOUT_UNAVAILABLE)
        if booking.hold_expires_at and booking.hold_expires_at <= timezone.now():
            raise ValidationError(GENERIC_CHECKOUT_UNAVAILABLE)
        if booking.service_id and not booking.service.is_active:
            raise ValidationError(GENERIC_CHECKOUT_UNAVAILABLE)

    @classmethod
    def _mark_payment_pending_if_needed(cls, booking, checkout_session, request_context=None):
        request_context = request_context or {}
        if checkout_session.status == CheckoutSession.Status.CREATED:
            transition_checkout(checkout_session, CheckoutSession.Status.PAYMENT_PENDING)
        if booking.status == Booking.Status.HELD:
            transition_booking(
                booking,
                Booking.Status.PAYMENT_PENDING,
                actor_type="system",
                reason="checkout_created",
                request_id=request_context.get("request_id"),
                metadata={"checkout_session_id": str(checkout_session.id)},
            )
        if booking.checkout_session_id != str(checkout_session.id):
            booking.checkout_session_id = str(checkout_session.id)
            booking.save(update_fields=["checkout_session_id", "updated_at"])

        _create_history(
            booking,
            "checkout_created",
            checkout_session.amount_snapshot,
            checkout_session.currency,
            checkout_session.id,
        )
        _create_history(
            booking, "payment_pending", checkout_session.amount_snapshot, checkout_session.currency, checkout_session.id
        )
        return booking

    @classmethod
    def mark_booking_payment_pending(cls, *, booking, checkout_session, request_context=None):
        with transaction.atomic():
            locked = Booking.objects.select_for_update().get(pk=booking.pk)
            session = CheckoutSession.objects.select_for_update().get(pk=checkout_session.pk)
            return cls._mark_payment_pending_if_needed(locked, session, request_context)

    @classmethod
    def confirm_booking_after_billing_success(cls, *, checkout_session, billing_ledger, request_context=None):
        request_context = request_context or {}
        with transaction.atomic():
            session = CheckoutSession.objects.select_for_update().get(pk=checkout_session.pk)
            if session.purchasable_type != "booking":
                raise ValidationError("Payment status could not be verified.")
            try:
                booking = Booking.objects.select_for_update().get(pk=session.purchasable_id)
            except (Booking.DoesNotExist, ValueError) as exc:
                raise ValidationError("Payment status could not be verified.") from exc
            snapshot = _price_snapshot(booking)
            billing_ledger = cls._validated_success_ledger(session, booking, billing_ledger, snapshot)
            if booking.status == Booking.Status.EXPIRED:
                return cls._record_manual_review_locked(
                    booking, session, billing_ledger, "payment_received_after_expiry"
                )
            if booking.status == Booking.Status.CONFIRMED:
                from bookings.services.receipts import ensure_confirmation_trust_artifacts_locked

                ensure_confirmation_trust_artifacts_locked(
                    booking=booking,
                    checkout_session=session,
                    billing_ledger=billing_ledger,
                )
                logger.info(
                    "booking.confirmation.duplicate_ignored",
                    extra={
                        "booking_public_id": str(booking.public_id),
                        "request_id": request_context.get("request_id"),
                    },
                )
                return booking
            if booking.status == Booking.Status.PAYMENT_FAILED:
                # A late success after a failed provider event is reconciled by
                # staff; auto-confirming could double-book a released slot.
                return cls._record_manual_review_locked(
                    booking,
                    session,
                    billing_ledger,
                    "payment_received_after_failure",
                )
            if booking.status != Booking.Status.PAYMENT_PENDING:
                raise ValidationError("Payment status could not be verified.")

            try:
                booking = transition_booking(
                    booking,
                    Booking.Status.CONFIRMED,
                    actor_type="system",
                    reason="billing_success",
                    request_id=request_context.get("request_id"),
                    metadata={"checkout_session_id": str(session.id), "billing_ledger_id": str(billing_ledger.id)},
                )
            except BookingStateError as exc:
                raise ValidationError("Payment status could not be verified.") from exc
            _create_history(
                booking, "payment_success", session.amount_snapshot, session.currency, session.id, billing_ledger.id
            )
            _create_history(
                booking, "booking_confirmed", session.amount_snapshot, session.currency, session.id, billing_ledger.id
            )
            from bookings.services.receipts import ensure_confirmation_trust_artifacts_locked

            ensure_confirmation_trust_artifacts_locked(
                booking=booking,
                checkout_session=session,
                billing_ledger=billing_ledger,
            )
            logger.info(
                "booking.confirmed",
                extra={
                    "booking_public_id": str(booking.public_id),
                    "checkout_public_hash": hash_sensitive_value(str(session.id))[:16],
                    "request_id": request_context.get("request_id"),
                },
            )
            return booking

    @staticmethod
    def _validated_success_ledger(session, booking, billing_ledger, snapshot):
        try:
            ledger = LedgerTransaction.objects.select_for_update().get(pk=billing_ledger.pk)
        except (AttributeError, LedgerTransaction.DoesNotExist, ValueError) as exc:
            raise ValidationError("Payment status could not be verified.") from exc

        if ledger.status != LedgerTransaction.Status.SUCCESS:
            raise ValidationError("Payment status could not be verified.")
        if str(ledger.external_correlation_id) != str(session.id):
            raise ValidationError("Payment status could not be verified.")
        if booking.checkout_session_id != str(session.id):
            raise ValidationError("Payment status could not be verified.")
        if session.purchasable_type != "booking" or session.purchasable_id != str(booking.id):
            raise ValidationError("Payment status could not be verified.")
        if session.amount_snapshot != snapshot.total_amount or session.currency != snapshot.currency:
            raise ValidationError("Payment status could not be verified.")
        if ledger.amount != snapshot.total_amount or ledger.currency != snapshot.currency:
            raise ValidationError("Payment status could not be verified.")
        return ledger

    @classmethod
    def fail_booking_after_payment_failure(cls, *, checkout_session, failure_reason, request_context=None):
        request_context = request_context or {}
        with transaction.atomic():
            session = CheckoutSession.objects.select_for_update().get(pk=checkout_session.pk)
            if session.purchasable_type != "booking":
                return None
            booking = Booking.objects.select_for_update().get(pk=session.purchasable_id)
            if booking.status == Booking.Status.CONFIRMED:
                return booking
            if booking.status in {Booking.Status.PAYMENT_FAILED, Booking.Status.EXPIRED}:
                return booking
            if booking.status != Booking.Status.PAYMENT_PENDING:
                raise ValidationError("Payment status could not be verified.")
            try:
                booking = transition_booking(
                    booking,
                    Booking.Status.PAYMENT_FAILED,
                    actor_type="system",
                    reason="payment_failed",
                    request_id=request_context.get("request_id"),
                    metadata={"failure_reason": str(failure_reason)[:64], "checkout_session_id": str(session.id)},
                )
            except BookingStateError as exc:
                raise ValidationError("Payment status could not be verified.") from exc
            _create_history(booking, "payment_failed", session.amount_snapshot, session.currency, session.id)
            return booking

    @classmethod
    def reconcile_late_payment_for_expired_hold(cls, *, checkout_session, billing_ledger, request_context=None):
        with transaction.atomic():
            session = CheckoutSession.objects.select_for_update().get(pk=checkout_session.pk)
            booking = Booking.objects.select_for_update().get(pk=session.purchasable_id)
            snapshot = _price_snapshot(booking)
            billing_ledger = cls._validated_success_ledger(session, booking, billing_ledger, snapshot)
            return cls._record_manual_review_locked(booking, session, billing_ledger, "payment_received_after_expiry")

    @staticmethod
    def _record_manual_review_locked(booking, session, billing_ledger, reason):
        # Booking financial history is operational evidence only; Billing
        # remains the immutable ledger truth.
        _create_history(
            booking,
            reason,
            session.amount_snapshot,
            session.currency,
            session.id,
            billing_ledger.id,
        )
        _create_history(
            booking,
            "requires_manual_review",
            session.amount_snapshot,
            session.currency,
            session.id,
            billing_ledger.id,
        )
        if not BookingAuditEvent.objects.filter(booking=booking, reason=reason).exists():
            BookingAuditEvent.objects.create(
                booking=booking,
                old_status=booking.status,
                new_status=booking.status,
                reason=reason,
                actor_type="system",
                metadata_redacted={"checkout_session_id": str(session.id), "manual_review_required": True},
            )
        logger.info(
            "booking.payment.manual_review_required",
            extra={"booking_public_id": str(booking.public_id), "reason": reason},
        )
        return booking
