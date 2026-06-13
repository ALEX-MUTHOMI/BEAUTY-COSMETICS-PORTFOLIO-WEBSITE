def redact_email(email: str) -> str:
    local, _, domain = str(email or "").partition("@")
    if not local or not domain:
        return "redacted-email"
    return f"{local[:1]}***@{domain}"
