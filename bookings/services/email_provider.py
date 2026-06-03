import base64
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from django.conf import settings

from billing.redaction import hash_sensitive_value

logger = logging.getLogger("bookings.email_provider")
FAKE_EMAIL_OUTBOX = []


class EmailProviderError(Exception):
    pass


@dataclass(frozen=True)
class EmailSendResult:
    accepted: bool
    provider: str
    provider_message_id: str


def _sanitize_header(value):
    return re.sub(r"[\r\n]+", " ", str(value or "")).strip()[:160]


def redact_email_error(value):
    value = re.sub(r"[\w.+-]+@[\w.-]+", "redacted-email", str(value or ""))
    value = re.sub(r"\+?254\d{9}\b", "redacted-phone", value)
    value = re.sub(r"(?i)(/[A-Za-z0-9._/-]+|[A-Za-z]:\\[^\s'\"<>]+)", "redacted-path", value)
    value = re.sub(r"(token|key|secret|bearer)[=: ]+[A-Za-z0-9_.:-]+", r"\1=redacted", value, flags=re.I)
    value = re.sub(r"\b[A-Za-z0-9_.]*-(token|key|secret)\b", "redacted-secret", value, flags=re.I)
    return value[:255]


def _validated_https_url(raw_url):
    parsed = urllib.parse.urlparse(str(raw_url or ""))
    if parsed.scheme != "https" or not parsed.netloc:
        raise EmailProviderError("Email provider URL must be HTTPS.")
    if parsed.username or parsed.password:
        raise EmailProviderError("Email provider URL must not include credentials.")
    return urllib.parse.urlunparse(parsed)


def _format_resend_attachments(attachments):
    formatted = []
    for attachment in attachments or []:
        filename = _sanitize_header(attachment.get("filename", "receipt.pdf")).replace("/", "-").replace("\\", "-")
        content = attachment.get("content", b"")
        if isinstance(content, str):
            content = content.encode()
        formatted.append(
            {
                "filename": filename[:120],
                "content": base64.b64encode(content).decode(),
                "content_type": attachment.get("content_type", "application/pdf"),
            }
        )
    return formatted


class FakeEmailProvider:
    provider = "fake"

    def send_email(self, *, to_hash, to_redacted, subject, html, text, attachments=None, metadata=None):
        subject = _sanitize_header(subject)
        message_id = hash_sensitive_value(f"{to_hash}:{subject}:{metadata or {}}")[:32]
        safe_attachments = []
        for attachment in attachments or []:
            content = attachment.get("content", b"")
            if isinstance(content, str):
                content = content.encode()
            safe_attachments.append(
                {
                    "filename": _sanitize_header(attachment.get("filename", "receipt.pdf")),
                    "content_type": attachment.get("content_type", "application/pdf"),
                    "size_bytes": len(content),
                    "sha256": attachment.get("sha256") or hash_sensitive_value(content),
                }
            )
        FAKE_EMAIL_OUTBOX.append(
            {
                "provider": self.provider,
                "recipient": to_redacted,
                "subject": subject,
                "attachments": safe_attachments,
                "metadata": {
                    key: str(value)
                    for key, value in (metadata or {}).items()
                    if key in {"booking_reference", "notification_type"}
                },
                "message_hash": message_id,
            }
        )
        logger.info("booking.email.fake_sent", extra={"recipient": to_redacted, "message_hash": message_id})
        return EmailSendResult(True, self.provider, f"fake-{message_id}")


def reset_fake_email_outbox():
    FAKE_EMAIL_OUTBOX.clear()


class ConsoleEmailProvider(FakeEmailProvider):
    provider = "console"


class ResendEmailProvider:
    provider = "resend"

    def send_email(self, *, to_hash, to_redacted, subject, html, text, attachments=None, metadata=None):
        api_key = getattr(settings, "EMAIL_PROVIDER_API_KEY", "")
        if not api_key:
            raise EmailProviderError("Email provider API key is not configured.")
        url = _validated_https_url(getattr(settings, "EMAIL_PROVIDER_BASE_URL", "https://api.resend.com/emails"))
        payload = {
            "from": getattr(settings, "EMAIL_FROM_ADDRESS", "no-reply@example.test"),
            "to": [getattr(settings, "EMAIL_EXTERNAL_TEST_RECIPIENT", to_redacted)],
            "reply_to": getattr(settings, "EMAIL_REPLY_TO_ADDRESS", ""),
            "subject": _sanitize_header(subject),
            "html": html,
            "text": text,
        }
        formatted_attachments = _format_resend_attachments(attachments)
        if formatted_attachments:
            payload["attachments"] = formatted_attachments
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(  # nosec B310 - URL is validated as HTTPS-only above.
                request, timeout=getattr(settings, "EMAIL_SEND_TIMEOUT_SECONDS", 5)
            ) as response:
                body = json.loads(response.read().decode() or "{}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise EmailProviderError(redact_email_error(exc)) from exc
        return EmailSendResult(True, self.provider, str(body.get("id") or hash_sensitive_value(body)[:32]))


class MailgunEmailProvider:
    provider = "mailgun"

    def send_email(self, *, to_hash, to_redacted, subject, html, text, attachments=None, metadata=None):
        api_key = getattr(settings, "EMAIL_PROVIDER_API_KEY", "")
        if not api_key:
            raise EmailProviderError("Email provider API key is not configured.")
        url = _validated_https_url(getattr(settings, "EMAIL_PROVIDER_BASE_URL", ""))
        if not url:
            raise EmailProviderError("Email provider base URL is not configured.")
        data = urllib.parse.urlencode(
            {
                "from": getattr(settings, "EMAIL_FROM_ADDRESS", "no-reply@example.test"),
                "to": getattr(settings, "EMAIL_EXTERNAL_TEST_RECIPIENT", to_redacted),
                "subject": _sanitize_header(subject),
                "html": html,
                "text": text,
            }
        ).encode()
        request = urllib.request.Request(url, data=data, method="POST")
        auth = base64.b64encode(f"api:{api_key}".encode()).decode()
        request.add_header("Authorization", f"Basic {auth}")
        try:
            with urllib.request.urlopen(  # nosec B310 - URL is validated as HTTPS-only above.
                request, timeout=getattr(settings, "EMAIL_SEND_TIMEOUT_SECONDS", 5)
            ) as response:
                body = response.read().decode()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise EmailProviderError(redact_email_error(exc)) from exc
        return EmailSendResult(True, self.provider, hash_sensitive_value(body)[:32])


def get_email_provider():
    provider = getattr(settings, "EMAIL_PROVIDER", "fake")
    if provider == "resend":
        return ResendEmailProvider()
    if provider == "mailgun":
        return MailgunEmailProvider()
    if provider == "console":
        return ConsoleEmailProvider()
    return FakeEmailProvider()
