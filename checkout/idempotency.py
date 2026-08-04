from billing.redaction import hash_sensitive_value


def build_idempotency_hash(value):
    return hash_sensitive_value(value)
