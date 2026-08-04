"""Guest-safe STK initiation bound to a held booking checkout (no session login)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking
from bookings.privacy import decrypt_value, hmac_phone_hash
from checkout.exceptions import CheckoutStateError, CheckoutValidationError
from checkout.models import CheckoutSession
from checkout.mpesa import normalize_mpesa_phone
from checkout.services import initiate_mpesa_stk

GENERIC_STK_ERROR = "Payment could not be started."
GENERIC_STK_UNAVAILABLE = "Payment is not available for this booking."


def initiate_guest_booking_stk(
    *,
    booking_public_id,
    checkout_public_id,
    phone_number,
    idempotency_key,
):
    """
    Fail-closed guest STK:

    - booking must own the checkout session (purchasable bind)
    - booking must be payment_pending (or held with matching checkout)
    - phone must match the booking customer phone (HMAC), not attacker-supplied MSISDN
    - checkout must not be terminal
    """
    if not booking_public_id or not checkout_public_id or not idempotency_key:
        raise ValidationError(GENERIC_STK_ERROR)

    try:
        normalized_request_phone = normalize_mpesa_phone(phone_number)
    except CheckoutValidationError as exc:
        raise ValidationError(GENERIC_STK_ERROR) from exc

    with transaction.atomic():
        try:
            booking = (
                Booking.objects.select_for_update(of=("self",))
                .select_related("customer_profile")
                .get(public_id=booking_public_id)
            )
        except Booking.DoesNotExist as exc:
            raise ValidationError(GENERIC_STK_UNAVAILABLE) from exc

        if booking.status not in {Booking.Status.PAYMENT_PENDING, Booking.Status.HELD}:
            raise ValidationError(GENERIC_STK_UNAVAILABLE)
        if booking.hold_expires_at and booking.hold_expires_at <= timezone.now():
            if booking.status == Booking.Status.HELD:
                raise ValidationError(GENERIC_STK_UNAVAILABLE)

        try:
            session = CheckoutSession.objects.select_for_update().get(pk=checkout_public_id)
        except (CheckoutSession.DoesNotExist, ValueError, TypeError) as exc:
            raise ValidationError(GENERIC_STK_UNAVAILABLE) from exc

        if session.purchasable_type != "booking" or session.purchasable_id != str(booking.id):
            raise ValidationError(GENERIC_STK_UNAVAILABLE)
        if booking.checkout_session_id and booking.checkout_session_id != str(session.id):
            raise ValidationError(GENERIC_STK_UNAVAILABLE)

        stored_phone = decrypt_value(booking.customer_profile.phone_encrypted)
        if hmac_phone_hash(stored_phone) != hmac_phone_hash(normalized_request_phone):
            raise ValidationError(GENERIC_STK_ERROR)

        try:
            attempt = initiate_mpesa_stk(
                session.id,
                phone_number=normalized_request_phone,
                idempotency_key=idempotency_key,
            )
        except CheckoutStateError as exc:
            raise ValidationError(GENERIC_STK_UNAVAILABLE) from exc
        except CheckoutValidationError as exc:
            raise ValidationError(GENERIC_STK_ERROR) from exc

        session.refresh_from_db(fields=["status"])

    return {
        "booking_public_id": str(booking.public_id),
        "checkout_public_id": str(session.id),
        "attempt_id": str(attempt.id),
        "payment_status": session.status,
        "next_action": "await_stk_confirmation",
    }
