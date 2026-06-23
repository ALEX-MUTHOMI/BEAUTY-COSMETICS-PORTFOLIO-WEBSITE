# Test Runtime Stability Guide

> Phase 3X-RL-CI is open pending current-tree matrix and GitHub Actions
> verification.

## Post-push CI Truth Rule

Run Docker Black, isort, Ruff, flake8, and `git diff --check` after all final
edits. Host Poetry evidence is invalid when its configured interpreter is
unavailable. A GitHub Actions failure reopens the related closeout until the
same tree passes locally and CI passes after an approved push.

## Canonical Test Partitions

| Partition | Command | Expected Duration | Timeout | Shard? |
|-----------|---------|-------------------|---------|--------|
| Security | `pytest tests/security -q` | < 300s | 600s | Full suite |
| Bookings | `pytest bookings/tests -q` | < 900s | 1200s | Full suite |
| Checkout + Billing | `pytest checkout/tests billing/tests -q` | < 400s | 600s | Full suite |
| API + Unit + Integration | `pytest tests/api tests/unit tests/integration -q` | < 120s | 300s | Full suite |
| Load | `pytest tests/load -q` | < 180s per shard | 300s | Bounded shards |
| Latency | `pytest tests/latency -q` | < 900s | 1200s | Full suite |

## Redis/Cache Cleanup Rules

### Django Cache
- Cleared automatically by `conftest._clear_test_cache` (autouse)
- Uses `django.core.cache.clear()`

### Direct Redis (Throttle + OTP)
- Cleared automatically by `conftest._flush_redis_throttle_keys` (autouse)
- Uses `SCAN` + `DELETE` for `throttle:*` and `otp:*` patterns
- **Critical**: `cache.clear()` does NOT clear these keys
- Any new direct-Redis usage must be added to this fixture

The fixture fails loudly in Docker/CI when Redis is expected. A fake Redis
outage test must scope its monkeypatch to the request so post-test cleanup uses
the real client again.

### When Adding New Redis Key Patterns
If you add a new feature that writes directly to Redis (not through Django cache):
1. Add the key pattern to `_flush_operational_redis_keys()` in `conftest.py`
2. Document the key pattern in this file
3. Verify cross-test isolation with `pytest --count=2` on affected tests

## Database Cleanup Rules

- pytest-django manages test DB lifecycle (create/destroy per session)
- Use `--reuse-db` for faster iteration (skips DB creation)
- `@pytest.mark.django_db` required for all DB-touching tests
- `TransactionTestCase` tests get full DB flush between tests (slower)
- Regular `TestCase` tests use transaction rollback (faster)

## Celery/Worker Rules

- Tests use `CELERY_TASK_ALWAYS_EAGER = True` by default
- No real worker needed for unit/integration tests
- Worker health verified by `docker compose ps` during smoke checks

## Diagnosing a Future Hang

1. **Identify the file**: Run profiler `docker compose exec -T web poetry run python scripts/ci/profile_security_matrix.py`
2. **Identify the test**: `pytest <file> -v --durations=10 --maxfail=1`
3. **Check Redis state**: `docker compose exec -T redis redis-cli DBSIZE` and `SCAN 0 MATCH throttle:*`
4. **Check DB sessions**: `docker compose exec -T db psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE datname LIKE 'test_%';"`
5. **Check stale processes**: `docker compose exec -T web ps aux | grep pytest`

## Phase Acceptance Criteria

A phase can be accepted only when:
1. All canonical partitions pass within their timeouts
2. No stale pytest processes remain after test runs
3. Redis key count returns to baseline after test runs
4. No test DB sessions remain idle-in-transaction
5. Lint/security/hygiene gates pass
