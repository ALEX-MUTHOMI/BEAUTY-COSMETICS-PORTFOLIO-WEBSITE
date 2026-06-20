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
.\scripts\ci\turbo_pass.ps1 -DockerConfigPath .\reports\ci\docker-config-empty
.\scripts\ci\turbo_pass.ps1 -VerboseOutput
```

`-SkipNewman` is for local developer iteration only. CI should run Docker
Newman through the canonical runner.

`-DockerConfigPath` is for Windows shells where the current user cannot read the
default Docker credential config. The script otherwise creates a repo-local
empty Docker config under `reports/ci/docker-config-empty` when `DOCKER_CONFIG`
is unset. This avoids credential-file ACL noise but does not hide Docker daemon
or named-pipe permission failures.

## Included Checks

- host git hygiene and tracked-artifact checks;
- Docker Compose config validation;
- security-scan Compose config validation;
- Django `check`;
- migration drift check;
- pytest collect-only;
- security headers and OpenAPI safety tests;
- Phase 3D deterministic route-throttle and abuse-response privacy tests;
- throttle malformed-body semantics tests;
- API/security tests, including Phase 3B/3B-C BOLA, IDOR, mass-assignment,
  role/header/query tampering, and deny-by-default authorization controls;
- unit/integration tests;
- Docker Newman acceptance;
- Black, isort, Ruff, flake8 fatal syntax gate;
- Bandit;
- filesystem secret hygiene;
- Docker health;
- Celery worker ping.

## Optional ZAP Passive Mode

Turbo Pass does not run full `all-passive` by default. The default lane keeps
Docker Newman standalone because it is faster and deterministic for API contract
coverage.

`-IncludeZapPassive` runs the bounded Newman-through-ZAP passive workflow, not
the full health/root/OpenAPI/Newman `all-passive` matrix. Use
`.\scripts\ci\run_security_passive_gate.ps1 -Mode all-passive` as the separate
passive security gate.

## Excluded Checks

Turbo Pass does not run full `tests/load`, full `tests/latency`, full
all-passive ZAP, Daraja sandbox tests, real email provider tests, real
storage-provider tests, active ZAP, Burp, or DDoS testing.

## Runtime Budget

Target local budget is 10-15 minutes where hardware allows. If the current
machine cannot meet that budget honestly, record the actual runtime in
`reports/ci/turbo-pass-summary.md` and use the partitioned matrix for deeper
verification.

## Failure Handling

The script fails fast. It does not hide failures, rewrite exits, delete tests,
or reduce assertions.

If Docker access fails, the expected diagnostic is:

```text
DOCKER_ACCESS_RESULT=failed
DOCKER_ACCESS_DIAGNOSTIC=Unable to reach Docker daemon from this shell...
```

That is a host Docker access issue, not a passing Turbo gate.

## Phase 3C-Final-E Record

The immediately preceding Phase 3C closeout sequence reported
`TURBO_PASS_RESULT=passed` in 699 seconds. The final 2026-06-20 passive gate
was intentionally run separately and completed in 502 seconds with
`FAIL-NEW=0`; this does not change Turbo Pass scope or make all-passive a
default Turbo step.
