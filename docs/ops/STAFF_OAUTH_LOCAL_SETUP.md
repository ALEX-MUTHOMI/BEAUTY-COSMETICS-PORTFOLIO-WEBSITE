# Staff Google / Apple OAuth — local & staging setup (1B)

**Option 2 (current product posture):** Password login is the reliable desk path. Google/Apple stay **fail-closed** until live credentials and `NUXT_PUBLIC_STAFF_*_ENABLED=true` are set. The login page never fakes a successful Google/Apple session.

Provisioned staff only. Never auto-create accounts from Google/Apple.

## Prerequisites

1. Staff email already created:
   `poetry run python manage.py create_staff_user --email you@gmail.com --password '…' --role receptionist`
2. Desk and API on the **same host** (local: `127.0.0.1`).
3. Secrets live only in `.env` / secret store — **never commit**.

## Google (Cloud Console)

1. Create OAuth 2.0 Client ID (Web application).
2. Authorized redirect URI:
   `http://127.0.0.1:8000/api/staff/auth/google/callback/`
   (staging: `https://<api-host>/api/staff/auth/google/callback/`)
3. Put in `.env`:

```env
STAFF_GOOGLE_OAUTH_CLIENT_ID=...
STAFF_GOOGLE_OAUTH_CLIENT_SECRET=...
STAFF_GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/staff/auth/google/callback/
STAFF_PORTAL_PUBLIC_ORIGIN=http://127.0.0.1:3000
NUXT_PUBLIC_STAFF_GOOGLE_ENABLED=true
```

4. Recreate web + frontend:
   `docker compose up -d --force-recreate web frontend`
5. Verify: `curl.exe http://127.0.0.1:8000/api/staff/auth/providers/` → `"google": true`
6. Open `http://127.0.0.1:3000/staff/login` — Continue with Google should navigate to Google.

## Apple (Developer)

1. Services ID + key; return URL:
   `http://127.0.0.1:8000/api/staff/auth/apple/callback/`
   (Apple often requires HTTPS for production; local HTTP may be limited.)
2. Put in `.env`:

```env
STAFF_APPLE_OAUTH_CLIENT_ID=...
STAFF_APPLE_OAUTH_CLIENT_SECRET=...   # JWT client secret
STAFF_APPLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/staff/auth/apple/callback/
NUXT_PUBLIC_STAFF_APPLE_ENABLED=true
```

3. Recreate services; providers → `"apple": true`.

## Fail-closed checks

| Condition | Expected |
|-----------|----------|
| Secrets empty | `providers` false; start URLs **404** |
| `.env.example` placeholders (`replace-with-*`) | Treated as empty — `providers` false; start **404** |
| Google email not provisioned | Redirect `?signin=unavailable`; audit `staff_not_provisioned` |
| Deactivated staff | Same as unprovisioned |
| Flag true but secrets empty | Button disabled / “almost ready” |
| Redirect URI mismatch vs GCP | Google `redirect_uri_mismatch` — fix GCP/env parity; do not thrash CSRF |

**G2 local redirect URI (byte-for-byte):**
`http://127.0.0.1:8000/api/staff/auth/google/callback/`

## Automated tests (no live IdP required)

```bash
docker compose exec web pytest bookings/tests/test_staff_oauth_callback.py tests/security/test_staff_auth_fortress_1b_2a.py -q
```
