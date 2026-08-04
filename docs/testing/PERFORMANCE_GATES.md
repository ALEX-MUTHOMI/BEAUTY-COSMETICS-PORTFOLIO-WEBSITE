# Performance Gates

Performance verification is split into explicit lanes. This avoids turning
`pytest` into a stale monolith while preserving deep coverage.

## Smoke

Command:

```powershell
.\scripts\ci\run_performance_gate.ps1 -Mode smoke
```

Purpose: fast representative checks for retry, timeout, and throttle behavior.
This does not replace full load tests.

## Standard

Command:

```powershell
.\scripts\ci\run_performance_gate.ps1 -Mode standard
```

Equivalent:

```powershell
docker compose exec -T web poetry run pytest tests/load -q --durations=25
docker compose exec -T web poetry run pytest tests/latency -q --durations=25
```

Observed local baseline from Phase 3A-P3:

- `tests/load`: 26 passed in about 18.5 minutes.
- `tests/latency`: 27 passed in about 1.75 minutes.

Combined load+latency is not canonical because it can exceed local command
budgets and obscure which partition is slow.

## Deep / Nightly

Deep and future heavier load belongs in scheduled or release-gated CI. Do not
weaken existing load tests to make the fast lane pass.

