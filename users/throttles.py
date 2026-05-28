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
        email = request.data.get("email", "").strip().lower()
        if not email:
            # Fallback to standard IP-only throttling if payload is malformed
            return self.get_ident(request)

        # Multi-factor throttle key
        return f"{self.get_ident(request)}:{email}"
