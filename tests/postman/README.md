# Beauty Backend API Acceptance Newman Suite

This collection verifies the backend as an external API product, not only as internal Django code.

It covers routing, CSRF bootstrap, cookie/session login, public catalog reads, booking availability and holds, checkout contract creation, fake M-Pesa webhook processing, public booking status, staff portal access, gallery reads, and security-negative response behavior.

## Local Docker

Seed deterministic fake data first:

```powershell
docker compose exec web poetry run python manage.py seed_api_acceptance_data
```

Run with host Newman:

```powershell
tests\postman\newman-run-local.cmd
```

Equivalent raw command:

```powershell
newman.cmd run tests\postman\beauty_backend_acceptance.postman_collection.json -e tests\postman\local-docker.postman_environment.json --bail --reporters cli,json --reporter-json-export tests\postman\reports\newman-local.json
```

## Security Boundaries

The local and staging-fake environments do not contain real Daraja, email-provider, R2, staff, or production secrets. Default runs must not call Daraja, Resend, Mailgun, or production object storage.

Generated JSON reports are ignored by Git. Keep `.gitkeep` only.

## Staging Fake

Use `staging-fake.postman_environment.example.json` as a placeholder template only. Copy it outside version control and replace placeholders on the staging host if this collection is used against a staging backend.
