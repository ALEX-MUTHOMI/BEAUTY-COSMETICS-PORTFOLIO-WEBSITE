import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, ReturningClientDevice
from bookings.privacy import decrypt_value
from bookings.services.holds import BookingHoldService

REMEMBER_DEVICE_CUSTOMER_COPY = (
    "Save my details on this device for faster booking next time. Sensitive actions still require verification."
)
GENERIC_REMEMBER_ERROR = "Remembered device is unavailable."


def cookie_name():
    return getattr(settings, "REMEMBER_DEVICE_COOKIE_NAME", "bc_remember_device")


def ttl_days():
    return int(getattr(settings, "REMEMBER_DEVICE_TTL_DAYS", 60))


def max_active_devices():
    return int(getattr(settings, "REMEMBER_DEVICE_MAX_ACTIVE_PER_CUSTOMER", 5))


def token_hash(token):
    token = str(token or "")
    if len(token) < 32:
        return ""
    return hash_sensitive_value(f"remember-device:{token}")


def _new_token():
    return secrets.token_urlsafe(48)


def _safe_profile_summary(profile):
    return {
        "display_name": profile.full_name_display,
        "email_redacted": profile.email_redacted,
        "phone_redacted": profile.phone_redacted,
    }


def _request_meta_hash(value):
    return hash_sensitive_value(value) if value else ""


def _expire_device(device, reason):
    device.status = ReturningClientDevice.Status.EXPIRED
    device.revoked_reason = reason[:64]
    device.revoked_at = timezone.now()
    device.save(update_fields=["status", "revoked_reason", "revoked_at", "updated_at"])


def issue_returning_device_token(
    *,
    customer_profile,
    ip="",
    user_agent="",
    enforce_device_limit=True,
):
    token = _new_token()
    now = timezone.now()
    expires_at = now + timezone.timedelta(days=ttl_days())
    with transaction.atomic():
        if enforce_device_limit:
            active_qs = (
                ReturningClientDevice.objects.select_for_update()
                .filter(customer_profile=customer_profile, status=ReturningClientDevice.Status.ACTIVE)
                .order_by("-created_at")
            )
            if active_qs.exists():
                active_qs.update(
                    status=ReturningClientDevice.Status.REVOKED,
                    revoked_at=now,
                    revoked_reason="rotated",
                    token_rotated_at=now,
                    updated_at=now,
                )
        device = ReturningClientDevice.objects.create(
            customer_profile=customer_profile,
            token_hash_hmac=token_hash(token),
            status=ReturningClientDevice.Status.ACTIVE,
            expires_at=expires_at,
            ip_hash_hmac=_request_meta_hash(ip),
            user_agent_hash_hmac=_request_meta_hash(user_agent),
            token_rotated_at=now,
        )
    return token, device


def lookup_returning_device(token):
    hashed = token_hash(token)
    if not hashed:
        return None
    device = (
        ReturningClientDevice.objects.select_related("customer_profile")
        .filter(token_hash_hmac=hashed, status=ReturningClientDevice.Status.ACTIVE)
        .first()
    )
    if device is None:
        return None
    if device.expires_at <= timezone.now() or device.customer_profile.erased_at:
        return None
    device.last_used_at = timezone.now()
    device.save(update_fields=["last_used_at", "updated_at"])
    return device


def remember_confirmed_booking(*, booking_public_id, remember_device, ip="", user_agent=""):
    if not remember_device:
        raise ValidationError(GENERIC_REMEMBER_ERROR)
    try:
        booking = Booking.objects.select_related("customer_profile").get(public_id=booking_public_id)
    except (Booking.DoesNotExist, TypeError, ValueError) as exc:
        raise ValidationError(GENERIC_REMEMBER_ERROR) from exc
    if booking.status != Booking.Status.CONFIRMED or booking.customer_profile.erased_at:
        raise ValidationError(GENERIC_REMEMBER_ERROR)
    token, _device = issue_returning_device_token(
        customer_profile=booking.customer_profile,
        ip=ip,
        user_agent=user_agent,
    )
    return token, _safe_profile_summary(booking.customer_profile)


def remembered_device_summary(token):
    device = lookup_returning_device(token)
    if device is None:
        return None
    return _safe_profile_summary(device.customer_profile)


def forget_returning_device(token):
    hashed = token_hash(token)
    if not hashed:
        return False
    with transaction.atomic():
        device = ReturningClientDevice.objects.select_for_update().filter(token_hash_hmac=hashed).first()
        if device is None:
            return False
        if device.status == ReturningClientDevice.Status.ACTIVE:
            device.status = ReturningClientDevice.Status.REVOKED
            device.revoked_at = timezone.now()
            device.revoked_reason = "customer_forget"
            device.save(update_fields=["status", "revoked_at", "revoked_reason", "updated_at"])
        return True


def create_hold_from_remembered_device(
    *,
    token,
    starts_at,
    idempotency_key,
    service_public_id=None,
    resource_public_id=None,
    full_package_public_id=None,
):
    device = lookup_returning_device(token)
    if device is None:
        raise ValidationError(GENERIC_REMEMBER_ERROR)
    profile = device.customer_profile
    payload = {
        "full_name": profile.full_name_display,
        "email": decrypt_value(profile.email_encrypted),
        "phone": decrypt_value(profile.phone_encrypted),
    }
    package_id = str(full_package_public_id or "").strip()
    service_id = str(service_public_id or "").strip()
    if package_id and service_id:
        raise ValidationError(GENERIC_REMEMBER_ERROR)
    if package_id:
        return BookingHoldService.create_full_package_hold(
            full_package_public_id=package_id,
            resource_public_id=resource_public_id,
            starts_at=starts_at,
            customer_payload=payload,
            idempotency_key=idempotency_key,
        )
    if not service_id:
        raise ValidationError(GENERIC_REMEMBER_ERROR)
    return BookingHoldService.create_bundle_hold(
        service_public_ids=[service_id],
        resource_public_id=resource_public_id,
        starts_at=starts_at,
        customer_payload=payload,
        idempotency_key=idempotency_key,
    )


def cleanup_expired_returning_devices(*, limit=500):
    now = timezone.now()
    ids = list(
        ReturningClientDevice.objects.filter(
            status=ReturningClientDevice.Status.ACTIVE,
            expires_at__lte=now,
        ).values_list("id", flat=True)[:limit]
    )
    updated = ReturningClientDevice.objects.filter(id__in=ids).update(
        status=ReturningClientDevice.Status.EXPIRED,
        revoked_at=now,
        revoked_reason="expired",
        updated_at=now,
    )
    return {"expired": updated}
