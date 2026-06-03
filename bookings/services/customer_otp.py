import secrets
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingNotification, CustomerActionSession, CustomerOTPChallenge
from bookings.privacy import hmac_email_hash, normalize_email

GENERIC_REQUEST_MESSAGE = "If the details are valid, we sent a code."
GENERIC_VERIFY_FAILURE = "Invalid or expired code."


@dataclass(frozen=True)
class OTPRequestResult:
    accepted: bool
    detail: str = GENERIC_REQUEST_MESSAGE


def _ttl_minutes():
    return int(getattr(settings, "CUSTOMER_OTP_TTL_MINUTES", 10))


def _max_attempts():
    return int(getattr(settings, "CUSTOMER_OTP_MAX_ATTEMPTS", 3))


def _request_limit():
    return int(getattr(settings, "CUSTOMER_OTP_REQUEST_LIMIT", 5))


def _action_session_ttl_minutes():
    return int(getattr(settings, "CUSTOMER_ACTION_SESSION_TTL_MINUTES", 15))


def _rate_key(*parts):
    return "booking:customer-otp:" + ":".join(hash_sensitive_value(part)[:16] for part in parts if part)


class CustomerOTPService:
    _last_test_code = ""

    @staticmethod
    def _generate_code():
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _rate_limited(*, recipient_hash, booking_public_id, ip_hash, user_agent_hash):
        keys = [
            _rate_key("recipient", recipient_hash),
            _rate_key("booking", str(booking_public_id)),
            _rate_key("ip", ip_hash),
            _rate_key("ua", user_agent_hash),
        ]
        for key in keys:
            count = cache.get(key, 0)
            if count >= _request_limit():
                return True
        for key in keys:
            cache.set(key, cache.get(key, 0) + 1, 600)
        return False

    @classmethod
    def request_challenge(cls, *, booking_public_id, email, purpose, request_meta=None):
        request_meta = request_meta or {}
        try:
            normalized_email = normalize_email(email)
        except Exception:
            return None
        recipient_hash = hmac_email_hash(normalized_email)
        ip_hash = hash_sensitive_value(request_meta.get("ip", ""))
        user_agent_hash = hash_sensitive_value(request_meta.get("user_agent", ""))

        if cls._rate_limited(
            recipient_hash=recipient_hash,
            booking_public_id=booking_public_id,
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
        ):
            return None

        try:
            booking = Booking.objects.select_related("customer_profile").get(public_id=booking_public_id)
        except (Booking.DoesNotExist, ValueError, TypeError):
            return None
        if booking.customer_profile.email_hash_hmac != recipient_hash or booking.customer_profile.erased_at:
            return None

        code = cls._generate_code()
        cls._last_test_code = code
        challenge = CustomerOTPChallenge.objects.create(
            purpose=purpose,
            booking=booking,
            recipient_hash_hmac=recipient_hash,
            otp_hash_hmac=hash_sensitive_value(code),
            expires_at=timezone.now() + timezone.timedelta(minutes=_ttl_minutes()),
            max_attempts=_max_attempts(),
            request_ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
        )
        BookingNotification.objects.update_or_create(
            booking=booking,
            notification_type=f"customer_otp_{purpose}",
            channel=BookingNotification.Channel.EMAIL,
            defaults={
                "recipient_email_hash": recipient_hash,
                "recipient_email_redacted": booking.customer_profile.email_redacted,
                "status": BookingNotification.Status.PENDING,
                "scheduled_for": timezone.now(),
                "failure_code": "",
                "last_error_redacted": "",
            },
        )
        return challenge

    @classmethod
    def verify_challenge(cls, public_id, code):
        try:
            with transaction.atomic():
                challenge = (
                    CustomerOTPChallenge.objects.select_for_update(of=("self",))
                    .select_related("booking")
                    .get(public_id=public_id)
                )
                if challenge.status != CustomerOTPChallenge.Status.PENDING:
                    return None
                if challenge.expires_at <= timezone.now():
                    challenge.status = CustomerOTPChallenge.Status.EXPIRED
                    challenge.save(update_fields=["status", "updated_at"])
                    return None
                if not secrets.compare_digest(challenge.otp_hash_hmac, hash_sensitive_value(code)):
                    challenge.attempts += 1
                    if challenge.attempts >= challenge.max_attempts:
                        challenge.status = CustomerOTPChallenge.Status.LOCKED
                    challenge.save(update_fields=["attempts", "status", "updated_at"])
                    return None

                challenge.status = CustomerOTPChallenge.Status.VERIFIED
                challenge.used_at = timezone.now()
                challenge.save(update_fields=["status", "used_at", "updated_at"])
                token = secrets.token_urlsafe(32)
                action = CustomerActionSession.objects.create(
                    token_hash=hash_sensitive_value(token),
                    purpose=challenge.purpose,
                    booking=challenge.booking,
                    expires_at=timezone.now() + timezone.timedelta(minutes=_action_session_ttl_minutes()),
                )
                action.token = token
                return action
        except (CustomerOTPChallenge.DoesNotExist, ValueError, TypeError):
            return None

    @staticmethod
    def consume_action_session(*, token, booking, purpose):
        token_hash = hash_sensitive_value(token)
        with transaction.atomic():
            session = (
                CustomerActionSession.objects.select_for_update()
                .filter(token_hash=token_hash, booking=booking, purpose=purpose, used_at__isnull=True)
                .first()
            )
            if session is None or session.expires_at <= timezone.now():
                return None
            session.used_at = timezone.now()
            session.save(update_fields=["used_at", "updated_at"])
            return session
