import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(
    name="users.tasks.send_express_otp_email",
    queue="express_auth",
    max_retries=3,
    default_retry_delay=5
)
def send_express_otp_email(email: str, otp: str) -> bool:
    """
    High-priority background Celery task to ship security verification codes.
    - Explicitly routed to the 'express_auth' queue to guarantee sub-10-second delivery boundaries.
    - Retries automatically on failure (e.g. SMTP connectivity drops).
    """
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
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'security@beautycosmetics.com')

    try:
        logger.info(f"[+] Dispatching OTP email task for: {email}...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False
        )
        logger.info(f"[+] OTP email dispatched successfully to: {email}")
        return True
    except Exception as exc:
        logger.error(f"[-] Failed to dispatch OTP email to {email}: {exc}")
        # Automatically retry the task in the background
        raise send_express_otp_email.retry(exc=exc)
