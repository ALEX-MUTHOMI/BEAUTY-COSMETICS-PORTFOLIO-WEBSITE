from core.throttling import RedisTokenBucketThrottle


class OTPAnonRateThrottle(RedisTokenBucketThrottle):
    """
    Rate throttle for OTP request (5/min via DEFAULT_THROTTLE_RATES["otp_request"]).
    Cache identity binds source IP and destination email (hashed later in allow_request).
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
