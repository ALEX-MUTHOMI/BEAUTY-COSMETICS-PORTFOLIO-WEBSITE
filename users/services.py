import hashlib
import hmac
import logging
import secrets
import string
from functools import lru_cache

import redis
import requests
from django.conf import settings

from users.redaction import redact_email

logger = logging.getLogger(__name__)


@lru_cache(maxsize=8)
def _redis_client(redis_url: str, connect_timeout: float, socket_timeout: float):
    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=connect_timeout,
        socket_timeout=socket_timeout,
        retry_on_timeout=False,
        health_check_interval=30,
    )


def get_redis_client():
    """
    Establish direct, pooled connection to the Redis Express Lane.
    Bypasses standard Django cache middleware to guarantee high-performance,
    un-cached transactional security for authentication codes.
    """
    return _redis_client(
        settings.REDIS_URL,
        float(getattr(settings, "REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS", 0.25)),
        float(getattr(settings, "REDIS_SOCKET_TIMEOUT_SECONDS", 0.5)),
    )


class OTPService:
    """
    Enterprise-grade Service Layer orchestrating Passwordless OTP Lifecycle
    and Cloudflare Turnstile bot mitigation challenges.
    """

    OTP_TTL_SECONDS = 300
    MAX_VERIFY_ATTEMPTS = 5

    @staticmethod
    def _normalized_email(email: str) -> str:
        """Return the stable identity representation used only inside HMAC input."""
        return str(email or "").strip().casefold()

    @classmethod
    def redis_key(cls, email: str) -> str:
        """Return a versioned OTP namespace without embedding recipient PII."""
        digest = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            f"express-otp-key:v1:{cls._normalized_email(email)}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"otp:express:v1:{digest}"

    @classmethod
    def _attempts_key(cls, email: str) -> str:
        digest = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            f"express-otp-attempts:v1:{cls._normalized_email(email)}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"otp:express:v1:attempts:{digest}"

    @classmethod
    def _code_digest(cls, email: str, code: str) -> str:
        """Store a verifier rather than a recoverable OTP value in Redis."""
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            f"express-otp-code:v1:{cls._normalized_email(email)}:{code}".encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def generate_otp(email: str) -> str:
        """
        Generates a cryptographically secure 6-digit OTP and persists it in Redis.
        - Uses secrets module for CSPRNG validation.
        - Stores a recipient-bound HMAC verifier under a non-PII key with a
          strict 300-second TTL.
        """
        otp = "".join(secrets.choice(string.digits) for _ in range(6))

        client = get_redis_client()
        key = OTPService.redis_key(email)

        # Save only a verifier. Redis keys and values must not expose recipient
        # PII or a reusable OTP if inspected by an authorized operator.
        client.set(key, OTPService._code_digest(email, otp), ex=OTPService.OTP_TTL_SECONDS)
        # A fresh OTP resets any prior brute-force attempt count for this recipient.
        client.delete(OTPService._attempts_key(email))
        logger.info("[+] Secure OTP generated and cached for email: %s", redact_email(email))
        return otp

    @staticmethod
    def verify_otp(email: str, code: str) -> bool:
        """
        Verifies the submitted OTP against Redis.
        - Instant Key Destruction (Replay Protection): Upon successful validation,
          the Redis key is deleted IMMEDIATELY, neutralizing replay attack vectors.
        - Bounded Guesses: A per-recipient failure counter locks out (destroys)
          the OTP after MAX_VERIFY_ATTEMPTS wrong codes, closing the brute-force
          window that would otherwise remain open for the full TTL.
        """
        client = get_redis_client()
        key = OTPService.redis_key(email)

        cached_verifier = client.get(key)
        if not cached_verifier:
            logger.warning("[-] OTP verification failed: Token expired or not found for %s", redact_email(email))
            return False

        if hmac.compare_digest(cached_verifier, OTPService._code_digest(email, code)):
            # Replay Protection: Instant key deletion
            client.delete(key)
            client.delete(OTPService._attempts_key(email))
            logger.info("[+] OTP verified successfully and key destroyed for %s", redact_email(email))
            return True

        attempts_key = OTPService._attempts_key(email)
        attempts = client.incr(attempts_key)
        if attempts == 1:
            client.expire(attempts_key, OTPService.OTP_TTL_SECONDS)
        if attempts >= OTPService.MAX_VERIFY_ATTEMPTS:
            # Too many wrong guesses: destroy the OTP outright rather than let
            # the remaining TTL be used for further brute-force attempts.
            client.delete(key)
            client.delete(attempts_key)
            logger.warning("[-] OTP locked after max failed attempts for %s", redact_email(email))
            return False

        logger.warning("[-] OTP mismatch detected for %s", redact_email(email))
        return False

    # Cloudflare's publicly documented "always passes" test secret. Real deployments
    # must override TURNSTILE_SECRET_KEY with a live secret, which also closes the
    # CF_CLEARANCE_TEST_TOKEN bypass below (it is only trusted while this placeholder
    # secret is still configured, i.e. dev/CI environments that never set a real one).
    _TURNSTILE_TEST_SECRET = "1x0000000000000000000000000000000AA"

    @staticmethod
    def verify_turnstile_token(token: str, remote_ip: str = None) -> bool:
        """
        Verifies Cloudflare Turnstile bot-mitigation tokens at the login boundary.
        - Standard challenge verify URL: https://challenges.cloudflare.com/turnstile/v0/siteverify
        - Bypasses check with a mock token 'CF_CLEARANCE_TEST_TOKEN', but ONLY while
          TURNSTILE_SECRET_KEY is still the Cloudflare test placeholder. Any real
          deployment must configure a live secret, which automatically disables this
          bypass without needing a separate environment flag.
        """
        turnstile_secret = getattr(settings, "TURNSTILE_SECRET_KEY", OTPService._TURNSTILE_TEST_SECRET)
        turnstile_is_in_test_mode = turnstile_secret == OTPService._TURNSTILE_TEST_SECRET

        if token == "CF_CLEARANCE_TEST_TOKEN":
            if not turnstile_is_in_test_mode:
                logger.error("[-] Rejected CF_CLEARANCE_TEST_TOKEN: a live Turnstile secret is configured.")
                return False
            if getattr(settings, "SECURITY_SCAN_MODE", False):
                logger.warning("[-] Turnstile verification blocked in security scan mode.")
                return False
            logger.info("[+] Test Turnstile token matched. Bypassing Turnstile challenge validation.")
            return True
        if getattr(settings, "SECURITY_SCAN_MODE", False):
            logger.warning("[-] Turnstile verification blocked in security scan mode.")
            return False
        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

        payload = {"secret": turnstile_secret, "response": token}
        if remote_ip:
            payload["remoteip"] = remote_ip

        try:
            response = requests.post(url, data=payload, timeout=5)
            result = response.json()
            success = result.get("success", False)
            if not success:
                logger.warning(f"[-] Turnstile verification rejected: {result.get('error-codes', [])}")
            return success
        except (requests.RequestException, ValueError):
            logger.error("[-] Cloudflare Turnstile challenge verification failed closed.")
            # In production, default-fail on API connection drops to maintain absolute perimeter integrity
            return False
