# Staff portal account provisioning (ops-only)

AestheticOS does **not** expose public staff registration. Staff accounts that can
view client bookings are created by ops.

## Create a staff user

From the Django/web container (or Poetry env with DB access):

```bash
poetry run python manage.py create_staff_user \
  --email owner@example.com \
  --password 'a long unique passphrase here' \
  --display-name 'Salon Owner'
```

Requirements:
- Password must pass staff policy (15+ characters, not common/predictable).
- User is created with `is_staff=True` and all `bookings` staff portal permissions.
- Login URL: `/staff/login`
- After login: `/staff/dashboard`
- Bookings table: `/staff/bookings`

## Password recovery

Staff can request a reset at `/staff/forgot-password`. The backend always returns
a generic success message. When email delivery is configured, the reset token is
issued via the staff password-reset outbox / provider path.

Confirm at `/staff/reset-password` with the token and a new policy-compliant password.

## Django admin

Superusers may also create staff via Django admin (`is_staff` + assign
`bookings.view_staff_*` permissions). Prefer `create_staff_user` for consistent
permission grants.

## Celery Beat (slot expiry — ops check)

Abandoned holds and checkout sessions must not lock the calendar forever.
Compose service `beat` runs:

- `bookings.tasks.sweep_stale_holds` (every 60s)
- `bookings.tasks.sweep_expired_checkouts` (every 60s)

Verify locally/staging:

```bash
docker compose ps beat
docker compose logs beat --tail=50
```

Expect the `beat` container to be `Up` and Celery Beat to log the schedule entries above.
