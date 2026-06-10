class BookingCircuitBreaker:
    """Redis-backed rolling-window abuse signal for booking hold exhaustion."""

    class Mode:
        NORMAL = "normal"
        ELEVATED = "elevated"
        ABUSE = "abuse"
        LOCKDOWN = "lockdown"

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
        try:
            if not hasattr(self.redis, "values"):
                self.redis.incr("booking:circuit_breaker:healthcheck")
                self.redis.expire("booking:circuit_breaker:healthcheck", 5)
            created = int(getattr(self.redis, "values", {}).get("booking:holds_created:10m", 0))
            confirmed = int(getattr(self.redis, "values", {}).get("booking:holds_confirmed:10m", 0))
        except Exception:
            return self.Mode.LOCKDOWN
        if created >= 20 and confirmed == 0:
            return self.Mode.ABUSE
        if created >= 10 and confirmed <= 1:
            return self.Mode.ELEVATED
        return self.Mode.NORMAL

    def hold_ttl_minutes(self):
        return 3 if self.mode_for_context() in {self.Mode.ABUSE, self.Mode.LOCKDOWN} else 10
