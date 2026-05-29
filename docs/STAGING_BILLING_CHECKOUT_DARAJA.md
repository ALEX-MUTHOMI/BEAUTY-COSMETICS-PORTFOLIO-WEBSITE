# Billing/Checkout Daraja Sandbox Staging Gate

This staging profile exists only to verify the Checkout -> Billing M-Pesa callback path with real Daraja sandbox traffic.
It is not a production deployment and must not be used with production credentials or customer data.

## Public Surface

Public routes:

- `GET /health/`: required for uptime checks and Daraja callback host preflight.
- `POST /api/checkout/mpesa/webhook/`: required for Daraja sandbox STK callback delivery.

Blocked routes:

- `/admin/*`: blocked at Caddy and removed from Django URL routing when `DISABLE_DJANGO_ADMIN=True`.
- `/api/auth/*`: blocked at Caddy.
- `/api/bookings/*`: blocked at Caddy.
- `/api/billing/*`: blocked at Caddy.
- `/api/checkout/sessions/*`: blocked at Caddy.
- all other `/api/*`: blocked at Caddy.
- all other routes: blocked at Caddy.

The staging flow uses `python manage.py verify_daraja_callback` from inside the `web` container to create a test checkout and initiate exactly one sandbox STK. Public checkout creation is intentionally not exposed.

## Stack

Services:

- `reverse-proxy`: Caddy, the only service with public ports `80` and `443`.
- `web`: Django/Gunicorn, exposed only on the Docker network.
- `worker`: Celery, exposed only on the Docker network.
- `db`: PostgreSQL, exposed only on the Docker network.
- `redis`: Redis, exposed only on the Docker network.

No frontend service is included. No database or Redis port is published.

## Environment

Create `.env.staging` from `.env.staging.example` on the staging host:

```bash
cp .env.staging.example .env.staging
```

Set real staging values only in `.env.staging`. Do not commit `.env.staging`.

Required security posture:

- `DEBUG=False`
- exact `ALLOWED_HOSTS`
- exact `CSRF_TRUSTED_ORIGINS`
- exact `CORS_ALLOWED_ORIGINS`
- `SECURE_SSL_REDIRECT=True`
- `DISABLE_DJANGO_ADMIN=True`
- `DRF_DISABLE_BROWSABLE_API=True`
- Daraja sandbox credentials only
- `PAYMENT_PROVIDER_MODE=fake`
- `CHECKOUT_MPESA_PROVIDER=fake`
- `DARAJA_REQUIRE_CALLBACK=true`
- `DARAJA_CALLBACK_WAIT_SECONDS=300`
- `DARAJA_TEST_MSISDN` set only in `.env.staging`

Never print or commit phone numbers, passkeys, generated passwords, tokens, receipts, checkout request IDs, merchant request IDs, or raw callback payloads.

## Deploy Staging

Validate compose:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging.example config -q
```

Start the stack:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
```

Check health:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging ps
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run python manage.py check
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run python manage.py makemigrations --check --dry-run
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run python manage.py migrate --noinput
curl -i https://staging-api.example.com/health/
```

Expected health response:

```json
{"status":"ok"}
```

## Synthetic Callback Preflight

Use a sanitized Daraja-shaped payload with fake IDs only. Do not use a real receipt, phone number, checkout request ID, or merchant request ID.

```bash
python - <<'PY'
import json
import urllib.error
import urllib.request

payload = {
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "fake-merchant-redacted",
            "CheckoutRequestID": "fake-checkout-redacted",
            "ResultCode": 1032,
            "ResultDesc": "Request cancelled by user",
        }
    }
}
req = urllib.request.Request(
    "https://staging-api.example.com/api/checkout/mpesa/webhook/",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        status = resp.status
except urllib.error.HTTPError as exc:
    status = exc.code
print("status", status)
print("non_500", status != 500)
PY
```

Expected:

- controlled non-500 response
- no IP allowlist failure
- no JSON parse error
- no ledger success

## Real Daraja Sandbox Callback Gate

Run exactly one real Daraja sandbox verification:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run python manage.py verify_daraja_callback
```

Rules:

- exactly one STK
- `DARAJA_TEST_AMOUNT=1`
- `DARAJA_TEST_MSISDN` from environment only
- user accepts the phone prompt
- wait up to 300 seconds
- no second STK if the first fails
- no real Daraja load test

Pass criteria:

- OAuth passes
- STK accepted by Daraja
- phone prompt initiated
- real callback received
- webhook inbox event exists
- checkout becomes `PAID`
- Billing creates exactly one `LedgerTransaction` with `SUCCESS`
- `FinancialAuditEvent` exists
- `SettlementRecord` exists or is pending
- duplicate replay does not double-credit
- logs are redacted

If Daraja returns 400, stop and report only the redacted diagnostic. If callback does not arrive, checkout remains pending, ledger success remains `0`, and production-candidate remains rejected.

## Post-Attempt Regression

Run inside staging after the real callback attempt:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run pytest checkout/tests billing/tests tests/security -vv
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run pytest
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run black --check .
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run isort --check-only .
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run ruff check .
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run bandit -r . -x tests -ll -ii
docker compose -f docker-compose.staging.yml --env-file .env.staging exec web poetry run python scripts/ci/secret_hygiene.py
```

Do not run real Daraja load tests.

## Production Readiness

Passing this staging sandbox gate can make Billing/Checkout production-candidate at code/integration level only. Full production readiness still requires production-like staging rehearsal, monitoring, alerting, credential rotation, refund/reversal runbooks, incident response, and an approved low-value live/canary payment reconciled end-to-end.
