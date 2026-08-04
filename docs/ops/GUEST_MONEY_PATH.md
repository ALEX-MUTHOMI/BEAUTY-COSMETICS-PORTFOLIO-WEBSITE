# Guest money path + Beat ops check

## Guest payment (no customer registration)

1. Customer picks date/slot on `/book`.
2. Checkout details: name, email (+ confirm), Kenya phone.
3. Backend: hold → booking checkout → **guest** STK at `POST /api/bookings/checkout/mpesa/stk/`.
4. Do **not** use `POST /api/checkout/sessions/<id>/mpesa/stk/` for guests (that route requires login).

## Beat

`docker compose` service `beat` must be running in staging/production so holds and
checkout sessions expire and free calendar capacity. See
[STAFF_PORTAL_PROVISIONING.md](./STAFF_PORTAL_PROVISIONING.md#celery-beat-slot-expiry--ops-check).
