import hashlib
import logging
import re
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import BookableResource, Booking, BookingAuditEvent, BookingPolicy, CustomerProfile, Service
from bookings.privacy import hmac_email_hash, hmac_phone_hash, normalize_email, normalize_phone
from bookings.services.availability import AvailabilityService
from bookings.services.circuit_breaker import BookingCircuitBreaker

BUSINESS_TZ = ZoneInfo("Africa/Nairobi")
UTC = ZoneInfo("UTC")
COUNTER_TTL_SECONDS = 600
GENERIC_UNAVAILABLE = "Availability unavailable."
logger = logging.getLogger("bookings.holds")


def _safe_text(value, max_length=80):
    cleaned = re.sub(r"<[^>]*>", "", str(value or ""))
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", cleaned)
    return " ".join(cleaned.split())[:max_length] or "Customer"


def _normalize_start(value):
    if value is None or timezone.is_naive(value):
        raise ValidationError(GENERIC_UNAVAILABLE)
    return value.astimezone(UTC).replace(second=0, microsecond=0)


def _fingerprint(*, service_id, resource_id, starts_at_utc, phone, email):
    material = "|".join(
        [
            str(service_id),
            str(resource_id),
            starts_at_utc.isoformat(),
            hmac_phone_hash(phone),
            hmac_email_hash(email),
        ]
    )
    return hashlib.sha256(material.encode()).hexdigest()


def _audit_fingerprint(booking):
    event = BookingAuditEvent.objects.filter(booking=booking, reason="hold_created").order_by("created_at", "id").last()
    if not event:
        return ""
    return event.metadata_redacted.get("request_fingerprint", "")


def _safe_counter(redis_client, key):
    if not redis_client:
        return
    try:
        redis_client.incr(key)
        redis_client.expire(key, COUNTER_TTL_SECONDS)
    except Exception:
        logger.info("booking.hold.redis_degraded", extra={"counter_key": key})


def _policy():
    return BookingPolicy.objects.order_by("-created_at").first() or BookingPolicy()


def _hold_ttl_minutes(policy, redis_client):
    mode = BookingCircuitBreaker(redis_client).mode_for_context() if redis_client else BookingCircuitBreaker.Mode.NORMAL
    if mode in {BookingCircuitBreaker.Mode.ABUSE, BookingCircuitBreaker.Mode.LOCKDOWN}:
        return policy.abuse_hold_minutes
    return policy.default_hold_minutes


def _available_for_start(service, resource, starts_at_utc):
    local_start = starts_at_utc.astimezone(BUSINESS_TZ)
    day = local_start.date()
    try:
        result = AvailabilityService.get_available_slots(service.id, day, day, resource_id=resource.id)
    except ValidationError as exc:
        raise ValidationError(GENERIC_UNAVAILABLE) from exc
    return any(slot["starts_at"] == local_start.isoformat() for slot in result[0]["slots"])


def _safe_response(booking, hold_ttl_minutes):
    local_start = booking.starts_at.astimezone(BUSINESS_TZ)
    local_end = booking.ends_at.astimezone(BUSINESS_TZ)
    local_expiry = booking.hold_expires_at.astimezone(BUSINESS_TZ) if booking.hold_expires_at else None
    return {
        "booking_public_id": str(booking.public_id),
        "status": booking.status,
        "hold_expires_at": local_expiry.isoformat() if local_expiry else None,
        "starts_at": local_start.isoformat(),
        "ends_at": local_end.isoformat(),
        "service_public_id": str(booking.service_id),
        "resource_public_id": str(booking.resource_id),
        "next_action": "checkout_required",
        "hold_ttl_minutes": hold_ttl_minutes,
    }


class BookingHoldService:
    @classmethod
    def create_hold(
        cls,
        *,
        service_public_id,
        resource_public_id=None,
        starts_at,
        customer_payload,
        idempotency_key,
        request_context=None,
    ):
        request_context = request_context or {}
        redis_client = request_context.get("redis_client")
        _safe_counter(redis_client, "booking:holds:attempted:10m")

        service, resource = cls._get_service_and_resource(service_public_id, resource_public_id)
        starts_at_utc = _normalize_start(starts_at)
        ends_at_utc = starts_at_utc + timedelta(minutes=service.duration_minutes)
        phone, email, full_name = cls._normalize_customer_payload(customer_payload)
        request_fingerprint = _fingerprint(
            service_id=service.id,
            resource_id=resource.id,
            starts_at_utc=starts_at_utc,
            phone=phone,
            email=email,
        )
        policy = _policy()
        ttl_minutes = _hold_ttl_minutes(policy, redis_client)

        try:
            with transaction.atomic():
                existing = Booking.objects.select_for_update().filter(idempotency_key=idempotency_key).first()
                if existing:
                    return cls._idempotent_response(existing, request_fingerprint, ttl_minutes)

                if not _available_for_start(service, resource, starts_at_utc):
                    raise ValidationError(GENERIC_UNAVAILABLE)

                customer = CustomerProfile.create_from_plaintext(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    reminder_consent=True,
                )
                booking = Booking.objects.create(
                    customer_profile=customer,
                    service=service,
                    resource=resource,
                    starts_at=starts_at_utc,
                    ends_at=ends_at_utc,
                    status=Booking.Status.HELD,
                    hold_expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
                    idempotency_key=idempotency_key,
                    privacy_policy_accepted_at=timezone.now(),
                    no_refund_policy_accepted_at=timezone.now(),
                )

                BookingAuditEvent.objects.create(
                    booking=booking,
                    old_status="",
                    new_status=Booking.Status.HELD,
                    reason="hold_created",
                    actor_type="customer",
                    request_id=request_context.get("request_id"),
                    metadata_redacted={
                        "request_fingerprint": request_fingerprint,
                        "circuit_breaker_mode": (
                            BookingCircuitBreaker(redis_client).mode_for_context()
                            if redis_client
                            else BookingCircuitBreaker.Mode.NORMAL
                        ),
                    },
                )
                _safe_counter(redis_client, "booking:holds:created:10m")
        except IntegrityError as exc:
            return cls._recover_integrity_conflict(idempotency_key, request_fingerprint, ttl_minutes, exc)

        logger.info(
            "booking.hold.created",
            extra={
                "booking_public_id": str(booking.public_id),
                "service_public_id": str(service.id),
                "resource_public_id": str(resource.id),
                "request_id": request_context.get("request_id"),
            },
        )
        return _safe_response(booking, ttl_minutes)

    @staticmethod
    def _get_service_and_resource(service_public_id, resource_public_id):
        try:
            service = Service.objects.filter(id=service_public_id, is_active=True).first()
            resource_query = BookableResource.objects.filter(is_active=True)
            resource = (
                resource_query.filter(id=resource_public_id).first() if resource_public_id else resource_query.first()
            )
        except (TypeError, ValueError):
            service = None
            resource = None
        if not service or not resource:
            raise ValidationError(GENERIC_UNAVAILABLE)
        return service, resource

    @staticmethod
    def _normalize_customer_payload(customer_payload):
        try:
            phone = normalize_phone(customer_payload.get("phone"))
            email = normalize_email(customer_payload.get("email"))
        except ValidationError as exc:
            raise ValidationError("Cannot complete booking hold.") from exc
        full_name = _safe_text(customer_payload.get("full_name"))
        return phone, email, full_name

    @staticmethod
    def _idempotent_response(existing, request_fingerprint, hold_ttl_minutes):
        if _audit_fingerprint(existing) != request_fingerprint:
            raise ValidationError("Idempotency conflict.")
        return _safe_response(existing, hold_ttl_minutes)

    @classmethod
    def _recover_integrity_conflict(cls, idempotency_key, request_fingerprint, hold_ttl_minutes, original_exc):
        existing = Booking.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return cls._idempotent_response(existing, request_fingerprint, hold_ttl_minutes)
        raise ValidationError(GENERIC_UNAVAILABLE) from original_exc
