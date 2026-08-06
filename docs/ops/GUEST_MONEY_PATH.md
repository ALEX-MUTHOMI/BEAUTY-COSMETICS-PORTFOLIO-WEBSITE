# Guest money path + Beat ops check

## Guest payment (no customer registration)

1. Customer picks date/slot on `/book`.
2. Checkout details: name, email (+ confirm), Kenya phone.
3. Backend: hold → booking checkout → **guest** STK at `POST /api/bookings/checkout/mpesa/stk/`.
4. Do **not** use `POST /api/checkout/sessions/<id>/mpesa/stk/` for guests (that route requires login).

## Beat

`docker compose` service `beat` must be running in staging/production so holds and
unpaid checkout sessions expire and free calendar capacity. See
[STAFF_PORTAL_PROVISIONING.md](./STAFF_PORTAL_PROVISIONING.md#celery-beat-slot-expiry--ops-check)
and [BACKEND_DSA_EFFICIENCY.md](../plan/BACKEND_DSA_EFFICIENCY.md).

Required schedule entries (`core/settings.py` `CELERY_BEAT_SCHEDULE`):

| Beat key | Task | Interval |
|----------|------|----------|
| `sweep-stale-booking-holds` | `bookings.tasks.sweep_stale_holds` | 60s |
| `sweep-expired-checkout-sessions` | `bookings.tasks.sweep_expired_checkouts` | 60s |

Hold expiry bumps calendar capacity generation so Redis cannot serve stale “full”
days after a hold times out.

Checkout expiry marks the checkout session expired and, for linked booking
purchases still in `payment_pending`, transitions the booking to `payment_failed`
(which also bumps capacity). It does not leave unpaid bookings blocking the day.
