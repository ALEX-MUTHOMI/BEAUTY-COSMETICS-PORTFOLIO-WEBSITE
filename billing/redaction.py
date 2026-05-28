import copy
import hmac
import re
from hashlib import sha256

from django.conf import settings

SENSITIVE_KEYS = {
    "phonenumber",
    "phone_number",
    "mpesareceiptnumber",
    "mpesa_receipt_number",
    "checkoutrequestid",
    "checkout_request_id",
    "merchantrequestid",
    "merchant_request_id",
    "access_token",
    "token",
}


def hash_sensitive_value(value):
    key = settings.SECRET_KEY.encode()
    return hmac.new(key, str(value).encode(), sha256).hexdigest()


def redact_phone(phone_number):
    value = str(phone_number)
    compact = value.replace(" ", "").replace("-", "")
    if len(compact) < 6:
        return "***"
    return f"{compact[:5]}***{compact[-3:]}"


def _redact_scalar(key, value):
    normalized_key = str(key).replace("-", "_").lower()
    if "phone" in normalized_key:
        return redact_phone(value)
    sensitive_tokens = ("receipt", "checkout", "merchant", "token")
    if normalized_key in SENSITIVE_KEYS or any(
        token in normalized_key for token in sensitive_tokens
    ):
        return f"redacted:{hash_sensitive_value(value)[:16]}"
    if isinstance(value, str):
        value = re.sub(
            r"\+?254[71]\d{8}", lambda match: redact_phone(match.group(0)), value
        )
    return value


def redact_financial_payload(payload):
    def redact(obj, parent_key=""):
        if isinstance(obj, dict):
            return {key: redact(value, key) for key, value in obj.items()}
        if isinstance(obj, list):
            return [redact(item, parent_key) for item in obj]
        return _redact_scalar(parent_key, obj)

    return redact(copy.deepcopy(payload or {}))
