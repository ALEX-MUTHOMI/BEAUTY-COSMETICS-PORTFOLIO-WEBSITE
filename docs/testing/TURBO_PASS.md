# Turbo Pass

Turbo Pass is the fast, deterministic verification lane for local and CI
preflight. It is designed to catch common regressions quickly without replacing
the full partitioned matrix.

## Command

```powershell
.\scripts\ci\turbo_pass.ps1
```

Optional local-only flags:

```powershell
.\scripts\ci\turbo_pass.ps1 -SkipNewman
.\scripts\ci\turbo_pass.ps1 -IncludeZapPassive
.\scripts\ci\turbo_pass.ps1 -VerboseOutput
```

`-SkipNewman` is for local developer iteration only. CI should run Docker
Newman through the canonical runner.

## Included Checks

- host git hygiene and tracked-artifact checks;
- Docker Compose config validation;
- security-scan Compose config validation;
- Django `check`;
- migration drift check;
- pytest collect-only;
- security headers and OpenAPI safety tests;
- throttle malformed-body semantics tests;
- API/security tests;
- unit/integration tests;
- Docker Newman acceptance;
- Black, isort, Ruff, flake8 fatal syntax gate;
- Bandit;
- filesystem secret hygiene;
- Docker health;
- Celery worker ping.

## Excluded Checks

Turbo Pass does not run full `tests/load`, full `tests/latency`, ZAP passive
scans, Daraja sandbox tests, real email provider tests, real storage-provider
tests, active ZAP, Burp, or DDoS testing.

## Runtime Budget

Target local budget is 10-15 minutes where hardware allows. If the current
machine cannot meet that budget honestly, record the actual runtime in
`reports/ci/turbo-pass-summary.md` and use the partitioned matrix for deeper
verification.

## Failure Handling

The script fails fast. It does not hide failures, rewrite exits, delete tests,
or reduce assertions.

