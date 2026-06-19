# CI Test Matrix

The canonical verification strategy is a partitioned matrix. The monolithic
`pytest -q` command is useful for local debugging but is not the primary CI gate
because it can exceed Docker Desktop runtime limits and leave stale test DB
connections when interrupted.

## Lane Overview

| Lane | Purpose | Command |
| --- | --- | --- |
| Turbo Pass | Fast local/CI preflight for common regressions | `.\scripts\ci\turbo_pass.ps1` |
| Standard Backend | Full domain partitions without load/ZAP | `.\scripts\ci\run_ci_matrix.ps1` |
| Performance | Load and latency with explicit budgets | `.\scripts\ci\run_performance_gate.ps1 -Mode standard` |
| Passive Security | Bounded ZAP health/root/OpenAPI/Newman passive scans | `.\scripts\ci\run_security_passive_gate.ps1 -Mode all-passive` |
| Deep/Nightly | Future slow dependency/deep load/security expansion | scheduled CI only |

## Canonical Gates

Run these as independent CI jobs or clearly separated local gates:

1. `docker compose config -q`
2. `docker compose -f docker-compose.yml -f docker-compose.security-scan.yml config -q`
3. `docker compose exec web poetry run python manage.py check`
4. `docker compose exec web poetry run python manage.py makemigrations --check --dry-run`
5. `docker compose exec web poetry run pytest --collect-only -q`
6. `docker compose exec web poetry run pytest tests/unit -q`
7. `docker compose exec web poetry run pytest tests/api -q`
8. `docker compose exec web poetry run pytest tests/security -q`
9. `docker compose exec web poetry run pytest tests/integration -q`
10. `docker compose exec web poetry run pytest bookings/tests -q`
11. `docker compose exec web poetry run pytest checkout/tests billing/tests -q`
12. `docker compose exec web poetry run pytest tests/load -q --durations=25`
13. `docker compose exec web poetry run pytest tests/latency -q --durations=25`
14. Docker Newman acceptance via `scripts/ci/run_newman_docker.ps1`.
15. ZAP passive health/root/OpenAPI/Newman scans through `scripts/ci/run_security_passive_gate.ps1 -Mode all-passive`.
16. `black --check .`
17. `isort --check-only .`
18. `ruff check .`
19. fatal-syntax `flake8`
20. `bandit`
21. `scripts/ci/secret_hygiene.py`

## Runtime Policy

Load and latency tests are intentionally separate from fast unit/API/security
gates. They are part of release confidence but should not starve faster jobs.
The standard performance lane runs them sequentially. Combined load+latency is
not canonical because it can exceed local command budgets and obscure which
partition caused a timeout.

## Monolithic Pytest Policy

`pytest -q` remains best-effort/debug. If it times out, do not weaken tests or
increase timeouts indefinitely. Use the partitioned matrix and inspect slow
partitions.

## Failure Handling

If a partition fails, fix that partition and rerun dependent gates. If an
interrupted run leaves `test_beauty_db` stale, use
`docs/testing/TEST_DB_LIFECYCLE.md`.

Generated reports are ignored by Git and may be uploaded as CI artifacts when
safe. Default CI must not call real Daraja, real email providers, production R2,
active ZAP, Burp, or real DDoS tooling.

## Authorization Security Gate

Phase 3B/3B-C authorization tests live in `tests/security` and are part of both
Turbo Pass and the standard `tests/api tests/security` matrix. The gate covers:

- customer-to-customer BOLA/IDOR;
- anonymous protected-object access;
- staff/non-staff/inactive-staff boundaries;
- mass assignment of owner/role/status/payment fields;
- role/header/query tampering;
- disabled legacy billing route behavior;
- public/private gallery query widening;
- deny-by-default for unknown sensitive routes.

No route that accepts object IDs, tokens, owner-like fields, role-like fields,
status-like fields, or payment-like fields may be added without updating the
authorization matrix and tests.
