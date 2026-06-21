# Security Matrix Root-Cause Report — Phase 3X

## Status: ROOT CAUSE IDENTIFIED AND FIXED

---

## Symptoms Observed

| Date Range | Symptom | Command |
|------------|---------|---------|
| Phase 3C late | `tests/security` took long but eventually passed | `pytest tests/security -q` |
| Phase 3D | `tests/security` timed out after 600s — no pass claimed | `pytest tests/security -q` |
| Phase 3D | Stale pytest processes left behind after timeout | Manual kill required |
| Phase 3D | Combined payment-load/latency exceeded timeout | Sequential sharding required |
| Phase 3C/3D | Host Git hygiene stalled on unbounded file scan | Script redesigned |

## Root Cause

**Redis throttle key pollution across tests.**

### Technical Details

The application uses two independent data stores that require independent cleanup:

1. **Django default cache** — cleared by `conftest._clear_test_cache` (autouse fixture)
2. **Direct Redis** — used by `core.throttling.RedisTokenBucketThrottle` via `users.services.get_redis_client()`

The throttle system **bypasses Django's cache framework entirely**. It uses a direct
`redis.Redis.from_url(settings.REDIS_URL)` connection with Lua-scripted token buckets.
The `cache.clear()` call in the existing conftest fixture only clears the Django cache
backend — it does **NOT** flush `throttle:*` keys from Redis.

### Failure Chain

```
1. Rate-limit test (e.g. test_rate_limit_route_controls.py) sends 10+ requests
2. Redis token bucket tokens consumed → throttle:scope:hash keys created
3. Keys persist with TTL of period*2 (120-172800 seconds)
4. All test clients share IP 127.0.0.1 → same hashed key
5. Subsequent tests hit throttled endpoints → get 429 responses
6. Tests expecting 200/403/404 fail or retry → cascading slowdown
7. 77 files × cumulative degradation → suite exceeds 600s timeout
```

### Evidence

| Test | Isolated Duration | In Suite (old) | In Suite (fixed) |
|------|-------------------|----------------|------------------|
| test_authorization_control_closeout.py | 44s | 180s+ (reported) | 23s setup + tests |
| Full `tests/security` (158 tests) | N/A | >600s (timeout) | **245s** |

### What Was NOT the Cause

- No individual test file is inherently slow (max 44s isolated)
- No `time.sleep()` calls in any security test
- No Celery task leakage
- No PostgreSQL session leak
- No ZAP containers running
- No blocking Redis calls (Lua script is atomic)
- No DB lock contention
- No test file ordering bug (cross-test pollution is order-independent)

## Fix Applied

### File: `conftest.py`

Added new `autouse=True` fixture `_flush_redis_throttle_keys` that:

1. Flushes all `throttle:*` and `otp:*` keys from direct Redis **before** each test
2. Flushes again **after** each test (belt-and-suspenders)
3. Uses `SCAN` (not `KEYS`) to avoid blocking Redis
4. Wrapped in `try/except` for non-Docker environments
5. Targets only operational test keys — does not touch Django cache or other Redis data

### Design Decision: Why Not `FLUSHDB`?

`FLUSHDB` would destroy Celery broker state, Django session data, and any other
Redis-backed services. The `SCAN`+`DELETE` pattern targets only throttle/OTP keys,
preserving Redis isolation for other subsystems.

## Contributing Causes (Not Root Cause)

1. **Combined slow gates under single timeout**: Payment-load + latency tests were
   previously run under one timeout. Fixed by bounded sharding in Phase 3D.
2. **Host Git hygiene unbounded scan**: Script scanned generated directories. Fixed
   by adding exclusion patterns.
3. **No stale process cleanup**: When outer runner timed out, child pytest processes
   were orphaned. Documented recovery procedure below.

## Stale Process Recovery Procedure

If a test run is interrupted:

```bash
# Inside web container — kill stale pytest
docker compose exec -T web pkill -f pytest || true

# Verify no stale DB sessions
docker compose exec -T db psql -U postgres -c \
  "SELECT pid, state, query_start FROM pg_stat_activity WHERE datname LIKE 'test_%';"

# Flush test throttle keys
docker compose exec -T web python -c "
from users.services import get_redis_client
c = get_redis_client()
for p in ('throttle:*', 'otp:*'):
    cursor = 0
    while True:
        cursor, keys = c.scan(cursor, match=p, count=200)
        if keys: c.delete(*keys)
        if cursor == 0: break
print('Flushed')
"
```

## Remaining Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| New throttle scopes added without test cleanup | Low | Fixture uses `throttle:*` wildcard pattern |
| Redis connection failure in fixture | Low | Silent `try/except` — tests proceed without flush |
| Future direct-Redis usage outside throttle/OTP | Medium | Document pattern in TEST_RUNTIME_STABILITY.md |
