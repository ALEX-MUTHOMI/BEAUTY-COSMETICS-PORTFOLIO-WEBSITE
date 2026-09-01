import base64
import hashlib
import hmac
import os
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_ON_ATTR = re.compile(r"(?i)\son[a-z]{1,32}\s*=\s*\S{1,200}")


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
    """Hash low-entropy phone numbers with keyed HMAC, never plain SHA256."""
    pepper = _required_secret("PII_HASH_PEPPER", getattr(settings, "PII_HASH_PEPPER", ""))
    return _hmac(normalize_phone(phone), pepper)


def hmac_email_hash(email):
    """Hash email lookup values with the same keyed-HMAC privacy boundary."""
    pepper = _required_secret("PII_HASH_PEPPER", getattr(settings, "PII_HASH_PEPPER", ""))
    return _hmac(normalize_email(email), pepper)


def _keystream(key, nonce, length):
    output = b""
    counter = 0
    while len(output) < length:
        output += hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        counter += 1
    return output[:length]


def encrypt_bytes(data):
    """Encrypt binary artifacts (receipt PDFs) with the booking PII key."""
    key = _required_secret("PII_ENCRYPTION_KEY", getattr(settings, "PII_ENCRYPTION_KEY", ""))
    payload = bytes(data)
    nonce = os.urandom(16)
    stream = _keystream(key, nonce, len(payload))
    ciphertext = bytes(a ^ b for a, b in zip(payload, stream, strict=True))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return nonce + tag + ciphertext


def decrypt_bytes(blob):
    key = _required_secret("PII_ENCRYPTION_KEY", getattr(settings, "PII_ENCRYPTION_KEY", ""))
    raw = bytes(blob)
    if len(raw) < 48:
        raise ValidationError("Encrypted value failed integrity validation.")
    nonce, tag, ciphertext = raw[:16], raw[16:48], raw[48:]
    expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise ValidationError("Encrypted value failed integrity validation.")
    stream = _keystream(key, nonce, len(ciphertext))
    return bytes(a ^ b for a, b in zip(ciphertext, stream, strict=True))


def encrypt_value(value):
    """Encrypt operational contact data needed later for reminders."""
    return base64.urlsafe_b64encode(encrypt_bytes(str(value).encode())).decode()


def decrypt_value(value):
    return decrypt_bytes(base64.urlsafe_b64decode(str(value).encode())).decode()


def strip_markup(value, max_length=None):
    """Linear HTML-tag strip for untrusted text. Avoids nested-regex ReDoS."""
    out = []
    in_tag = False
    for ch in str(value or ""):
        if ch == "<":
            in_tag = True
            continue
        if ch == ">":
            in_tag = False
            continue
        if not in_tag:
            out.append(ch)
    cleaned = _ON_ATTR.sub(" ", "".join(out))
    cleaned = _CONTROL_CHARS.sub(" ", cleaned)
    cleaned = " ".join(cleaned.split())
    if max_length is not None:
        cleaned = cleaned[:max_length]
    return cleaned


_JS_PAYLOAD_TOKENS = ("javascript:", "onerror", "onload", "script", "alert")


def neutralize_script_payload(text):
    """Linear, case-insensitive drop of leftover JS tokens after tag strip."""
    result = str(text or "")
    guard = 0
    while guard < 32:
        guard += 1
        lower = result.lower()
        hit = -1
        token = ""
        for candidate in _JS_PAYLOAD_TOKENS:
            idx = lower.find(candidate)
            if idx != -1 and (hit == -1 or idx < hit):
                hit = idx
                token = candidate
        if hit == -1:
            break
        end = hit + len(token)
        if token == "alert" and end < len(result) and result[end] == "(":
            close = result.find(")", end, end + 80)
            end = close + 1 if close != -1 else min(end + 80, len(result))
        result = result[:hit] + result[end:]
    return " ".join(result.split())


def safe_display_name(full_name):
    """Return dashboard-safe display text without exposing full raw PII."""
    cleaned = strip_markup(full_name)
    parts = [part for part in cleaned.split() if part]
    if not parts:
        return "Customer"
    if len(parts) == 1:
        return parts[0][:24]
    return f"{parts[0][:24]} {parts[-1][0]}."
