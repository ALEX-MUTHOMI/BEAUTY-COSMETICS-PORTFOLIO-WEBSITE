class BookingCircuitBreaker:
    """Redis-backed rolling-window abuse signal for booking hold exhaustion."""

    class Mode:
        NORMAL = "normal"
        ELEVATED = "elevated"
        ABUSE = "abuse"
        LOCKDOWN = "lockdown"

    # These must match the counter keys actually written by
    # bookings.services.holds._safe_counter (and the confirmation-side
    # counter incremented on booking confirmation). A prior mismatch here
    # ("holds_created" vs "holds:created") meant this breaker always read
    # zero and never escalated in production.
    CREATED_KEY = "booking:holds:created:10m"
    CONFIRMED_KEY = "booking:holds:confirmed:10m"

    def __init__(self, redis_client=None, window_seconds=600):
        self.redis = redis_client
        self.window_seconds = window_seconds

    def incr(self, key):
        # Every increment refreshes expiry so attack counters cannot become
        # permanent locks after traffic normalizes.
        value = self.redis.incr(key)
        self.redis.expire(key, self.window_seconds)
        return value

    def mode_for_context(self):
        # PostgreSQL aggregate scans are intentionally avoided on this path;
        # the booking perimeter needs a cheap fail-safe signal during attack.
        # A real Redis client (or any spec-compliant test double) must be
        # read via .get(); never rely on internal client attributes.
        try:
            created = int(self.redis.get(self.CREATED_KEY) or 0)
            confirmed = int(self.redis.get(self.CONFIRMED_KEY) or 0)
        except Exception:
            return self.Mode.LOCKDOWN
        if created >= 20 and confirmed == 0:
            return self.Mode.ABUSE
        if created >= 10 and confirmed <= 1:
            return self.Mode.ELEVATED
        return self.Mode.NORMAL

    def hold_ttl_minutes(self):
        return 3 if self.mode_for_context() in {self.Mode.ABUSE, self.Mode.LOCKDOWN} else 10
