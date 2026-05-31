import base64
import hashlib
import hmac
import os
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError


def _required_secret(name, value):
    if value:
        return value.encode()
    if getattr(settings, "DEBUG", False):
        return b"debug-only-booking-secret"
    raise ImproperlyConfigured(f"{name} is required for booking PII protection.")


def normalize_phone(phone):
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    if digits.startswith("7") and len(digits) == 9:
        digits = "254" + digits
    if not digits.startswith("254") or len(digits) != 12:
        raise ValidationError("Invalid Kenyan phone number.")
    return f"+{digits}"


def redact_phone(phone):
    normalized = normalize_phone(phone)
    return f"{normalized[:5]}***{normalized[-3:]}"


def normalize_email(email):
    email = (email or "").strip().lower()
    if "@" not in email:
        raise ValidationError("Invalid email.")
    return email


def redact_email(email):
    email = normalize_email(email)
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _hmac(value, pepper):
    return hmac.new(pepper, value.encode(), hashlib.sha256).hexdigest()


def hmac_phone_hash(phone):
    pepper = _required_secret("PII_HASH_PEPPER", getattr(settings, "PII_HASH_PEPPER", ""))
    return _hmac(normalize_phone(phone), pepper)


def hmac_email_hash(email):
    pepper = _required_secret("PII_HASH_PEPPER", getattr(settings, "PII_HASH_PEPPER", ""))
    return _hmac(normalize_email(email), pepper)


def _keystream(key, nonce, length):
    output = b""
    counter = 0
    while len(output) < length:
        output += hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        counter += 1
    return output[:length]


def encrypt_value(value):
    key = _required_secret("PII_ENCRYPTION_KEY", getattr(settings, "PII_ENCRYPTION_KEY", ""))
    nonce = os.urandom(16)
    data = value.encode()
    stream = _keystream(key, nonce, len(data))
    ciphertext = bytes(a ^ b for a, b in zip(data, stream, strict=True))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + tag + ciphertext).decode()


def decrypt_value(value):
    key = _required_secret("PII_ENCRYPTION_KEY", getattr(settings, "PII_ENCRYPTION_KEY", ""))
    raw = base64.urlsafe_b64decode(value.encode())
    nonce, tag, ciphertext = raw[:16], raw[16:48], raw[48:]
    expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise ValidationError("Encrypted value failed integrity validation.")
    stream = _keystream(key, nonce, len(ciphertext))
    return bytes(a ^ b for a, b in zip(ciphertext, stream, strict=True)).decode()


def safe_display_name(full_name):
    parts = [part for part in (full_name or "").strip().split() if part]
    if not parts:
        return "Customer"
    if len(parts) == 1:
        return parts[0][:24]
    return f"{parts[0][:24]} {parts[-1][0]}."
