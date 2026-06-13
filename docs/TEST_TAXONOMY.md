# Test Taxonomy — Beauty SaaS Backend

## Test Organization

| Directory                | Count | Focus Area                                      | Partition Command                                          |
|--------------------------|-------|--------------------------------------------------|------------------------------------------------------------|
| `bookings/tests/`        | 290   | Domain models, services, selectors, views        | `pytest bookings/tests -q`                                 |
| `checkout/tests/`        | 66    | Checkout session lifecycle, Daraja, webhooks      | `pytest checkout/tests -q`                                 |
| `billing/tests/`         | 25    | Ledger lifecycle, financial audit, redaction      | `pytest billing/tests -q`                                  |
| `tests/api/`             | 3     | Backend API acceptance contract                  | `pytest tests/api -q`                                      |
| `tests/integration/`     | 33    | Full lifecycle (booking→checkout→billing→receipt) | `pytest tests/integration -q`                              |
| `tests/security/`        | 80    | Red team (auth, billing, holds, checkout, gallery)| `pytest tests/security -q`                                 |
| `tests/load/`            | 26    | Hold pressure, checkout storm, webhook storm     | `pytest tests/load -vv --durations=25`                     |
| `tests/latency/`         | 27    | Kenya network latency simulation, timeouts       | `pytest tests/latency -vv --durations=25`                  |
| `tests/unit/`            | 11    | Auth and user unit tests                         | `pytest tests/unit -q`                                     |
| `tests/external/`        | 4     | Daraja sandbox, email provider sandbox           | `pytest tests/external --run-external -q`                  |
| `tests/postman/`         | —     | Postman collection + environments                | Newman CLI                                                 |

## Auto-Markers (conftest.py)

Tests are automatically marked based on their directory path:

| Path Pattern         | Markers Applied                        |
|----------------------|----------------------------------------|
| `tests/load/`        | `payment_load`                         |
| `tests/security/`    | `payment_security`                     |
| `tests/latency/`     | `latency`, `network_resilience`        |
| `tests/integration/` | `payment_contract`                     |
| Contains `daraja`    | `payment_contract`                     |
| Marked `external`    | Skipped unless `--run-external` passed |

## Partitioned Verification Protocol

The canonical CI strategy is the partitioned matrix documented in
`docs/testing/CI_TEST_MATRIX.md`. A monolithic `pytest -q` run is best-effort
local diagnostics only; it is not the primary gate because interrupted long runs
can leave stale test DB sessions. If that happens, use
`docs/testing/TEST_DB_LIFECYCLE.md`.

Run these in order. If any partition fails, stop and investigate before continuing.
Do not run these partitions in parallel against the same Docker Postgres test
database unless a separate isolated test database strategy is configured.

### Quick Smoke (< 2 min)
```bash
docker compose exec web poetry run pytest bookings/tests -q --tb=short
docker compose exec web poetry run pytest tests/api -q --tb=short
```

### Integration + Security (< 5 min)
```bash
docker compose exec web poetry run pytest tests/integration -q --tb=short
docker compose exec web poetry run pytest tests/security -q --tb=short
```

### Checkout + Billing (< 3 min)
```bash
docker compose exec web poetry run pytest checkout/tests -q --tb=short
docker compose exec web poetry run pytest billing/tests -q --tb=short
```

### Load + Latency (≤ 10 min)
```bash
docker compose exec web poetry run pytest tests/load -vv --durations=25
docker compose exec web poetry run pytest tests/latency -vv --durations=25
```

### Import/Compilation Gates
```bash
docker compose exec web poetry run pytest --collect-only -q
docker compose exec web poetry run python -m compileall bookings checkout billing
```

### Lint/Security/Formatting Gates
```bash
docker compose exec web poetry run black --check .
docker compose exec web poetry run isort --check-only .
docker compose exec web poetry run ruff check .
docker compose exec web poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
docker compose exec web poetry run bandit -r . -x tests -ll -ii
```

## Test Location Convention

Tests for a module follow this pattern:

| Module Path                        | Test Path                                |
|------------------------------------|------------------------------------------|
| `bookings/selectors/booking_status.py` | `bookings/tests/test_booking_status_endpoint.py` |
| `bookings/domain/circuit_breaker.py`   | `bookings/tests/test_booking_hold_abuse_circuit_breaker.py` |
| `bookings/infrastructure/email_provider.py` | `bookings/tests/test_email_provider_contract.py` |
| `bookings/gallery/selectors/public_gallery.py` | `bookings/tests/test_gallery_public_output_contract.py` |
| `checkout/services.py`                 | `checkout/tests/test_checkout_session_lifecycle.py` |

**Note**: Test files have NOT been relocated in this phase. They remain in their
original directories. Some tests still import stable compatibility wrappers;
canonical factory ownership is now under `tests/factories/`.

## Fixture Ownership

- Root `conftest.py` is limited to global safety fixtures, pytest markers, and
  external-test gating.
- External provider tests remain skipped unless `--run-external` is supplied.
- Gallery storage tests use per-test temporary storage and must not write to
  production media paths.
- `tests/factories/booking_factories.py` owns shared booking, service, resource,
  and customer-profile factories.
- `bookings/tests/factories.py` is a compatibility wrapper for old imports.
- Do not put provider secrets, real phone numbers, raw receipt tokens, checkout
  IDs, or storage keys in factory defaults.
- Booking date/time fixtures must explicitly choose business-policy-compatible
  days unless the test is intentionally asserting Tuesday/Wednesday/full-package
  or closed-day behavior.
