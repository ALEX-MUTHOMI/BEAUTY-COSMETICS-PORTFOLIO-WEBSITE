import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _redact_email(email):
    local, _, domain = str(email).partition("@")
    if not domain:
        return "redacted-email"
    return f"{local[:2]}***@{domain}"


@shared_task(
    name="users.tasks.send_express_otp_email",
    queue="express_auth",
    max_retries=3,
    default_retry_delay=5,
)
def send_express_otp_email(email: str, otp: str, correlation_id: str = None) -> bool:
    """
    High-priority background Celery task to ship security verification codes.
    - Explicitly routed to the 'express_auth' queue to guarantee sub-10-second delivery boundaries.
    - Retries automatically on failure (e.g. SMTP connectivity drops).
    """
    redacted_email = _redact_email(email)
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
        f"Beauty Portfolio & Booking Team"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "security@beautycosmetics.com")

    try:
        logger.info(
            "[+] Dispatching OTP email task for: %s correlation_id=%s...",
            redacted_email,
            correlation_id,
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
        logger.error("[-] Failed to dispatch OTP email to %s", _redact_email(email))
        # Automatically retry the task in the background
        raise send_express_otp_email.retry(exc=exc) from exc
