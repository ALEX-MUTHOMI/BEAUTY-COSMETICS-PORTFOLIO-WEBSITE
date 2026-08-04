import json
from collections.abc import Mapping, Sequence

AUTH_KEY_MARKERS = {
    "access_token",
    "api_key",
    "csrf",
    "otp",
    "passkey",
    "password",
    "refresh_token",
    "reset_token",
    "secret",
    "sessionid",
    "token_hash",
    "verification_token",
}

PAYMENT_PROVIDER_KEY_MARKERS = {
    "billing_ledger_id",
    "callback_payload",
    "checkout_request_id",
    "checkoutrequestid",
    "ledger_id",
    "merchant_request_id",
    "merchantrequestid",
    "mpesa_receipt",
    "mpesareceiptnumber",
    "provider_payload",
    "provider_reference_hash",
    "raw_payload",
}

STORAGE_KEY_MARKERS = {
    "bucket",
    "exif",
    "original_private_key",
    "private_key",
    "quarantine_key",
    "r2",
    "sha256",
    "signed_url",
    "storage_key",
}

INTERNAL_DEBUG_KEY_MARKERS = {
    "__dict__",
    "_state",
    "database_id",
    "debug",
    "deleted_at",
    "exception",
    "internal_id",
    "owner_id",
    "sql",
    "stack",
    "traceback",
}

KNOWN_TEST_PII_VALUES = {
    "+254712345678",
    "grace@example.com",
}

TRACEBACK_VALUE_MARKERS = {
    "Traceback",
    "Internal Server Error",
    "ValidationError",
    "DoesNotExist",
    "IntegrityError",
    "ProgrammingError",
    "SELECT ",
}


def response_payload(response):
    content_type = response.headers.get("Content-Type", "")
    body = response.content.decode("utf-8", errors="replace")
    if "application/json" not in content_type:
        return body
    try:
        return json.loads(body or "{}")
    except json.JSONDecodeError:
        return body


def _walk(value, path="$"):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_path = f"{path}.{key}"
            yield key_path, key, child
            yield from _walk(child, key_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def assert_no_forbidden_keys(payload, markers, *, allowed_keys=()):
    allowed = {item.lower() for item in allowed_keys}
    marker_set = {item.lower() for item in markers}
    violations = []
    for path, key, _child in _walk(payload):
        key_text = str(key).lower()
        if key_text in allowed:
            continue
        for marker in marker_set:
            if marker in key_text:
                violations.append((path, marker))
    assert not violations, f"forbidden response key categories found: {violations}"


def assert_no_sensitive_values(payload, markers):
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    violations = [marker for marker in markers if marker and marker in rendered]
    assert not violations, f"forbidden response value markers found: {violations}"


def assert_response_excludes_categories(response, *, categories, allowed_keys=(), forbidden_values=()):
    payload = response_payload(response)
    markers = set()
    for category in categories:
        markers.update(category)
    assert_no_forbidden_keys(payload, markers, allowed_keys=allowed_keys)
    assert_no_sensitive_values(payload, set(forbidden_values) | TRACEBACK_VALUE_MARKERS)
    return payload
