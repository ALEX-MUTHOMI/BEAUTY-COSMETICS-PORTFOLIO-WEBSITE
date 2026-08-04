# Test Database Lifecycle

The Django test database is disposable, but cleanup must be scoped tightly.
Never clean development, staging, production, or manually curated data.

## Known Failure Mode

Interrupted monolithic pytest runs can leave connections open against
`test_aesthetic_os_db`. A later test run may fail with:

- duplicate test database creation;
- database already exists;
- database is being accessed by other users;
- deadlocks during teardown flush.

This is a test-runtime lifecycle issue, not application-data corruption.

## Safe Cleanup Script

Use:

```powershell
docker compose exec web poetry run python scripts/ci/cleanup_test_db_sessions.py
```

The default mode is dry-run. It prints only:

- target test database name;
- whether the target is recognized as a test database;
- planned actions.

It does not print credentials.

## Terminate Stale Test Sessions

Use only after confirming the target database starts with `test_` or ends with
`_test`:

```powershell
docker compose exec web poetry run python scripts/ci/cleanup_test_db_sessions.py --terminate-sessions --yes-i-understand-this-targets-only-the-test-db
```

## Drop Stale Test Database

Use only when the test DB is contaminated by an interrupted run:

```powershell
docker compose exec web poetry run python scripts/ci/cleanup_test_db_sessions.py --terminate-sessions --drop-test-db --yes-i-understand-this-targets-only-the-test-db
```

The script refuses to target system databases or names that are not clearly test
databases.

## Prohibited Cleanup

Do not:

- drop the app database;
- drop staging or production databases;
- kill sessions without a test DB name guard;
- make cleanup automatic in normal app startup;
- print DB credentials.

## CI Guidance

Ephemeral CI should prefer fresh test databases. Local developers can use the
cleanup script after interrupted test runs.
