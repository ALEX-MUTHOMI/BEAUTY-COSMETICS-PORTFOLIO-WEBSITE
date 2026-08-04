# Staff portal account provisioning (ops-only)

AestheticOS does **not** expose public staff registration. Staff accounts that can
view client bookings are created by ops (**Auth Fortress 1B**).

**Locked model**

1. Owner provisions first (`create_staff_user` + role).
2. Staff signs in at unlisted `/staff/login` with **password and/or Google** (Google only if OAuth env is ready and the email is already `is_staff`).
3. Django issues an HttpOnly session; every `/api/staff/*` enforces session + RBAC.
4. Public chrome must **not** link to `/staff` (**2A**). `robots.txt` disallows `/staff`. Gates are session/RBAC — not secret URLs.

Do **not** hardcode shared salon passwords or invent “dynamic passwords in the browser.”

## Local HTTP session posture (auth boundary)

Staff login uses Django **session + CSRF** cookies (`sessionid` HttpOnly,
`csrftoken` for the SPA header). Cookie `Secure` flags follow
`SECURE_SSL_REDIRECT` in `core/settings.py` (when `DEBUG=False`).

| Environment | `SECURE_SSL_REDIRECT` | Cookie `Secure` (default) |
|-------------|----------------------|---------------------------|
| Local compose / HTTP desk | **`False`** (compose default) | Off — browser can send cookies on HTTP |
| Staging / production TLS | **`True`** (see `.env.staging.example`) | On — HTTPS only |

**Host alignment (CSRF SameSite=Strict):** open the desk and API on the **same host name**.
Prefer local `http://127.0.0.1:3000` with `NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
and `STAFF_PORTAL_PUBLIC_ORIGIN=http://127.0.0.1:3000`. Mixing `localhost` and `127.0.0.1`
drops Strict CSRF cookies and looks like a login failure.

**Ops rule:** local HTTP desks **require** `SECURE_SSL_REDIRECT=False`. Staging/prod must keep
redirect + Secure cookies on. Prefer a **same-origin API edge** behind TLS in production.

## Create a staff user

From the Django/web container (or Poetry env with DB access):

```bash
poetry run python manage.py create_staff_user \
  --email owner@example.com \
  --password 'a long unique passphrase here' \
  --display-name 'Salon Owner' \
  --role owner
```

```bash
poetry run python manage.py create_staff_user \
  --email desk@example.com \
  --password 'a long unique passphrase here' \
  --role receptionist

poetry run python manage.py create_staff_user \
  --email artist@example.com \
  --password 'a long unique passphrase here' \
  --role beautician
```

| Role | Receipt PDF | Payments desk | Confirm attendance | Assign beautician | Schedule scope |
|------|-------------|---------------|--------------------|-------------------|----------------|
| owner | Yes | Yes | Yes | Yes | All |
| receptionist | No | No | Yes | Yes | All |
| beautician | No | No | No | No | Assigned only |

Deactivating a staff user in Django admin ends password **and** Google login for that email
(`is_active=False` / not `is_staff`). Existing sessions expire via idle/absolute timeouts
(and logout).

## Google OAuth (1B — provisioned emails only)

Google is **implemented** but **off** until configured. It never auto-provisions accounts.

**Staging enable recipe**

1. Create OAuth client (Web) with redirect URI
   `https://<api-host>/api/staff/auth/google/callback/`
   (local: `http://127.0.0.1:8000/api/staff/auth/google/callback/`).
2. Set on `web` (and matching secrets store):
   - `STAFF_GOOGLE_OAUTH_CLIENT_ID`
   - `STAFF_GOOGLE_OAUTH_CLIENT_SECRET`
   - `STAFF_GOOGLE_OAUTH_REDIRECT_URI`
   - (defaults already cover AUTH_URL / TOKEN_URL)
3. Set `NUXT_PUBLIC_STAFF_GOOGLE_ENABLED=true` on the frontend **only after**
   `GET /api/staff/auth/providers/` returns `"google": true`.
4. Provision the staffer’s Google email with `create_staff_user` **before** first Google login.
5. Keep `NUXT_PUBLIC_STAFF_APPLE_ENABLED=false` unless Apple is fully configured later.

Unprovisioned Google accounts redirect to `/staff/login?signin=unavailable` and audit
`reason=staff_not_provisioned`. Password login remains available for desk resilience.

## Password recovery

Staff can request a reset at `/staff/forgot-password`. The backend always returns
a generic success message. Confirm at `/staff/reset-password` with the token and a
new policy-compliant password.

## Discoverability (2A)

- No public nav/footer link to `/staff/login`.
- Staff pages emit `noindex,nofollow`.
- `frontend/public/robots.txt` includes `Disallow: /staff`.
- Strangers who guess the URL only see the login box; APIs still require staff session + RBAC.

## Security variables matrix

| Variable | Local desk | Staging/prod | Failure mode if wrong |
|----------|------------|--------------|------------------------|
| `SECURE_SSL_REDIRECT` | `False` | `True` | Cookies not stored → CSRF/login stall |
| `REDIS_URL` / Redis password | Must match compose | Must match | Fail-closed **503** on CSRF/login |
| `GUNICORN_WORKERS` | `1` under ~1G | Scale with RAM | OOM death spiral → multi-hour desk down |
| `NUXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000` | Same-origin or HTTPS API | Host mismatch → CSRF 403 |
| `STAFF_PORTAL_PUBLIC_ORIGIN` | `http://127.0.0.1:3000` | Public Nuxt origin | Bad OAuth `next` redirects |
| `STAFF_GOOGLE_OAUTH_*` | Empty until ready | Set together | Start returns 404; button stays disabled |
| `NUXT_PUBLIC_STAFF_GOOGLE_ENABLED` | `false` until providers ready | `true` with OAuth | UI/API mismatch |
| `NUXT_PUBLIC_STAFF_APPLE_ENABLED` | `false` | `false` unless Apple ready | Leave off |
| `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` | Include desk origin | Include desk origin | Browser blocks credentialed calls |

## Attacker-view checklist

| Attack | Control |
|--------|---------|
| Brute force password | Route throttle + login cooldown; generic 400; audits |
| Google account stuffing | Provision gate — no `is_staff` → no session |
| Guess `/staff/login` | Login UI only; `/api/staff/*` denied without session |
| Bypass UI hide (beautician → receipt) | Django permission on receipt PDF / payments |
| Redis outage | Fail-closed 503 + Retry-After — availability, not data leak |
| Mass-assign `is_staff` | Rejected on public APIs (security tests) |

## Django admin

Superusers may also create staff via Django admin (`is_staff` + permissions). Prefer
`create_staff_user` for consistent role grants.

## Celery Beat (slot expiry — ops check)

Abandoned holds and checkout sessions must not lock the calendar forever.
Compose service `beat` runs:

- `bookings.tasks.sweep_stale_holds` (every 60s)
- `bookings.tasks.sweep_expired_checkouts` (every 60s)

After Redis flaps, restart **Celery workers separately** — staff login must not depend on Celery health.

```bash
docker compose ps beat worker
docker compose logs beat --tail=50
```

## Docker security gate (auth fortress)

```bash
docker compose exec web pytest \
  tests/security/test_staff_auth_fortress_1b_2a.py \
  tests/security/test_staff_portal_owasp_red_team.py \
  tests/load/test_redis_failure_safety.py \
  bookings/tests/test_staff_oauth_callback.py \
  bookings/tests/test_staff_login_endpoint.py \
  bookings/tests/test_staff_portal_rbac.py \
  -q
```
