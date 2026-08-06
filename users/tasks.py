import binascii
import json
import logging

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from bookings.privacy import decrypt_value, encrypt_value
from users.redaction import redact_email

logger = logging.getLogger(__name__)


def build_express_otp_delivery_payload(email: str, otp: str) -> str:
    """Encrypt OTP delivery data before it enters the Celery broker payload."""
    return encrypt_value(json.dumps({"email": str(email), "otp": str(otp)}, separators=(",", ":")))


def _load_express_otp_delivery_payload(encrypted_payload: str) -> tuple[str, str]:
    """Decrypt and validate the minimal delivery fields inside the worker only."""
    try:
        payload = json.loads(decrypt_value(str(encrypted_payload)))
        email = str(payload["email"])
        otp = str(payload["otp"])
    except (binascii.Error, KeyError, TypeError, UnicodeDecodeError, ValidationError, ValueError) as exc:
        raise ValueError("Invalid encrypted OTP delivery payload.") from exc
    if not email or not otp:
        raise ValueError("Invalid encrypted OTP delivery payload.")
    return email, otp


@shared_task(
    name="users.tasks.send_express_otp_email",
    queue="express_auth",
    max_retries=3,
    default_retry_delay=5,
)
def send_express_otp_email(encrypted_payload: str, correlation_id: str | None = None) -> bool:
    """
    High-priority background Celery task to ship security verification codes.
    - Explicitly routed to the 'express_auth' queue to guarantee sub-10-second delivery boundaries.
    - Accepts only an encrypted payload so Redis-backed Celery transport never
      carries a raw recipient or reusable OTP.
    - Accepts the framework's server-generated correlation context for task
      compatibility, but does not log or include it in delivery content.
    - Retries automatically on failure (e.g. SMTP connectivity drops).
    """
    try:
        email, otp = _load_express_otp_delivery_payload(encrypted_payload)
    except ValueError:
        logger.error("[-] Rejected invalid encrypted OTP delivery payload")
        return False

    redacted_email = redact_email(email)
    if getattr(settings, "EMAIL_PROVIDER", "fake").strip().lower() == "fake":
        # Local/CI fake mode must be fast and non-networked. The task boundary
        # remains exercised without turning an OTP test into SMTP retries.
        logger.info("[+] Fake OTP email dispatch accepted for: %s", redacted_email)
        return True

    subject = "Your Secure Booking Verification Code"
    message = (
        f"Hello,\n\n"
        f"Your secure 6-digit verification code is: {otp}\n\n"
        f"This code will expire in 5 minutes (300 seconds). "
        f"For security, never share this code with anyone.\n\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Regards,\n"
        f"AestheticOS Team"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "security@aesthetic-os.example.com")

    try:
        logger.info(
            "[+] Dispatching encrypted OTP email task for: %s",
            redacted_email,
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("[+] OTP email dispatched successfully to: %s", redacted_email)
        return True
    except Exception as exc:
        logger.error("[-] Failed to dispatch OTP email to %s", redact_email(email))
        # Automatically retry the task in the background
        raise send_express_otp_email.retry(exc=exc) from exc
