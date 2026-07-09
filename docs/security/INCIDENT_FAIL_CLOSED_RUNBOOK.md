# Incident fail-closed runbook (real-money booking)

## Principles
1. Prefer availability of **safe denial** over unsafe success.
2. Fake payment providers must never run in production.
3. Daraja live callbacks stay opt-in (`workflow_dispatch` + GitHub Environment).

## Money-path kill switches
| Signal | Action |
|--------|--------|
| Hold spam / bot wave | Abuse escalation → Turnstile required (`hold_bot_guard`); throttle `booking_hold` |
| Status enumeration | Throttle `booking_status` (20/min); generic 404 bodies |
| Origin/Host spoof | CORS allowlist + `ALLOWED_HOSTS`; reject unknown Host with 400 |
| Provider outage | Keep `PAYMENT_PROVIDER_MODE=fake` out of prod; queue notifications |

## CI fail-safes
- Fail-fast tiers: lint → units → **payment-security** → integration → Newman/ZAP → load → chaos
- `concurrency` cancels superseded pushes
- Job `timeout-minutes` prevent hung runners
- `permissions: contents: read` (CICD-SEC-5)
- Only `daraja-sandbox-contract` may skip on push

## Certification checklist gates
- frontend-backend-trust (origin/CORS/CSRF/Host)
- privacy-redaction (Sentry scrubbers + status minimization)
- payment-security red-team partition
- Toxiproxy chaos after load

## First response checklist
1. Confirm provider mode and callback allowlists.
2. Raise abuse circuit / require Turnstile.
3. Rotate leaked secrets; scrub Sentry if DSN active.
4. Preserve CI artifacts for forensics; do not force-push over evidence.
