# Secret Hygiene Policy

Secret hygiene has two separate responsibilities.

## Host / CI Git Hygiene

Run:

```powershell
.\scripts\ci\git_hygiene_host.ps1
```

This lane owns repository/index-aware checks:

- tracked `.env` and `db.sqlite3` detection;
- generated Newman/ZAP/CI report ignore checks;
- `git diff --check`;
- high-confidence secret/debug assignment markers in tracked files.

It does not print secret values.

## Container Filesystem Hygiene

Run:

```powershell
docker compose exec -T web poetry run python scripts/ci/secret_hygiene.py
```

This scans the container filesystem. It may not be git-index aware if `git` is
not installed in the runtime image.

## Runtime Image Policy

Do not install `git` into the production/runtime image unless there is a proven
runtime need. Git-aware hygiene belongs on the host or CI runner.

