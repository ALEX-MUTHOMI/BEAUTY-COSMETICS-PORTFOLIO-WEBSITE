# Logging and Diagnostics Policy

`BEAUTY_DIAGNOSTIC_TRACE` is disabled by default and is enabled only for local
debugging or CI when explicitly set. It is not enabled by production defaults.

When enabled, request diagnostics record a route name, method, status family,
latency, retry hint, actor type, and hashed request/actor/client identifiers.
Throttle diagnostics record scope, configured rate, decision, remaining token
count, retry hint, Redis outcome, and failure behavior.

Each request receives a server-generated correlation ID. Incoming
`X-Request-ID` values are deliberately ignored so client-controlled text cannot
be reflected into response headers, structured logs, or task metadata.

Django request warnings are rewritten to a status code and resolved route name
before console output. This prevents a path UUID, opaque handle, query string,
or client-controlled malformed path from being recorded in application logs.

Never logged: request or response bodies, query strings, phone numbers, email
addresses, tokens, sessions, checkout/ledger/provider identifiers, storage keys,
media paths, bucket names, or raw Redis keys. Diagnostics use the normal
application logger; no raw diagnostic artifact is written to the repository.
