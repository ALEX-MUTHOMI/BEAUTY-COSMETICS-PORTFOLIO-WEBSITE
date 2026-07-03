from core.throttling import RedisTokenBucketThrottle


class OTPAnonRateThrottle(RedisTokenBucketThrottle):
    """
    Advanced Enterprise Rate Throttle to mitigate email toll fraud.
    - Rate is limited to 5 requests per hour.
    - Multi-Factor Cache Key: Binds both the client's source IP address and
      the targeted destination email address.
    - Prevents:
      1. Distributed Spamming: Attacker using IP proxies to flood a single email address.
      2. Domain Spraying: Attacker using a single IP address to spray spam to multiple emails.
    """

    scope = "otp_request"

    def get_cache_ident(self, request, view):
        # Retrieve target email from request payload
        data = request.data if hasattr(request.data, "get") else {}
        email = str(data.get("email", "")).strip().lower()
        if not email:
            # Fallback to standard IP-only throttling if payload is malformed
            return self.get_ident(request)

        # Multi-factor throttle key
        return f"{self.get_ident(request)}:{email}"


class OTPVerifyRateThrottle(RedisTokenBucketThrottle):
    """
    Bounds guess velocity against /api/auth/verify-otp/.

    A 6-digit OTP has only 1,000,000 possible values. Without a request-rate
    ceiling here, an attacker with a valid target email could exhaust the
    space well within the OTP's TTL window. This is layered on top of the
    per-recipient failure-lockout in OTPService.verify_otp (defense in depth:
    IP+email throttle stops fast/scripted attempts, the lockout counter stops
    slow/distributed ones).
    """

    scope = "otp_verify"

    def get_cache_ident(self, request, view):
        data = request.data if hasattr(request.data, "get") else {}
        email = str(data.get("email", "")).strip().lower()
        if not email:
            return self.get_ident(request)
        return f"{self.get_ident(request)}:{email}"
