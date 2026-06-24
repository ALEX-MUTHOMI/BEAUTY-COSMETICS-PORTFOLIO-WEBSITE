from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from core.celery import app as celery_app
from users.services import OTPService
from users.tasks import send_express_otp_email

User = get_user_model()


class MockRedis:
    """
    In-memory Mock Redis implementation for offline unit testing velocity.
    Supports basic SET, GET, DELETE, EXISTS, and TTL operations.
    """

    def __init__(self):
        self.store = {}
        self.ttls = {}

    def set(self, key, value, ex=None):
        self.store[key] = str(value)
        if ex:
            self.ttls[key] = int(ex)
        return True

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        if key in self.store:
            del self.store[key]
            if key in self.ttls:
                del self.ttls[key]
            return 1
        return 0

    def exists(self, key):
        return 1 if key in self.store else 0

    def ttl(self, key):
        return self.ttls.get(key, -1)

    def eval(self, _script, key_count, *keys_and_args):
        """Emulate the bounded Redis token-bucket contract used at runtime."""
        keys = keys_and_args[:key_count]
        args = keys_and_args[key_count:]
        key = keys[0]
        now, capacity, refill_rate, ttl = args[:4]
        bucket_key = f"bucket:{key}"
        bucket = self.store.get(bucket_key)
        now = float(now)
        capacity = float(capacity)
        refill_rate = float(refill_rate)
        if bucket is None:
            tokens = capacity
            updated_at = now
        else:
            tokens, updated_at = bucket
        tokens = min(capacity, tokens + max(0, now - updated_at) * refill_rate)
        allowed = 1 if tokens >= 1 else 0
        wait_seconds = 0
        if allowed:
            tokens -= 1
        else:
            wait_seconds = int((1 - tokens) / refill_rate) + 1
        self.store[bucket_key] = (tokens, now)
        self.ttls[bucket_key] = int(ttl)

        if key_count == 1:
            return [allowed, tokens, wait_seconds]

        score_key, action_key = keys[1:]
        (
            score_window,
            cooldown_score,
            temporary_ban_score,
            waf_score,
            cooldown_seconds,
            ban_seconds,
            waf_seconds,
            early_retry,
        ) = args[4:]
        action = self.store.get(action_key, "normal")
        if action != "normal":
            score = int(self.store.get(score_key, 0)) + int(early_retry)
            self.store[score_key] = score
            self.ttls[score_key] = int(score_window)
            return [0, 0, max(self.ttl(action_key), 1), score, action, 1, 0]

        if allowed:
            return [1, tokens, 0, 0, "normal", 0, 0]

        score = int(self.store.get(score_key, 0)) + 1
        self.store[score_key] = score
        self.ttls[score_key] = int(score_window)
        next_action = "normal"
        action_ttl = 0
        if score >= int(waf_score):
            next_action, action_ttl = "waf_candidate", int(waf_seconds)
        elif score >= int(temporary_ban_score):
            next_action, action_ttl = "temporary_ban", int(ban_seconds)
        elif score >= int(cooldown_score):
            next_action, action_ttl = "cooldown", int(cooldown_seconds)
        if next_action != "normal":
            self.store[action_key] = next_action
            self.ttls[action_key] = action_ttl
            wait_seconds = max(wait_seconds, action_ttl)
        return [0, tokens, wait_seconds, score, next_action, 0, int(next_action != "normal")]


@pytest.fixture(autouse=True)
def mock_redis_backend():
    """
    Autouse fixture that dynamically patches users.services.get_redis_client
    to return a singleton MockRedis instance during test execution.
    """
    mock_client = MockRedis()
    with patch("users.services.get_redis_client", return_value=mock_client):
        yield mock_client


@pytest.fixture(autouse=True)
def eager_celery():
    """
    Autouse fixture to force Celery to run tasks synchronously in memory
    rather than dispatching to an active AMQP broker.
    """
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False


@pytest.fixture
def api_client():
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    return client


@pytest.fixture
def client_ip():
    return "192.168.1.100"


@pytest.mark.django_db
class TestPasswordlessAuthSuite:
    """
    Exhaustive Test-Driven Development (TDD) Suite verifying
    cryptographic boundaries, replay protections, rate limits, and compliance gates.
    """

    # --------------------------------------------------------------------------
    # 1. REDIS TTL EXPIRATION TEST
    # --------------------------------------------------------------------------
    def test_otp_redis_ttl_expiration(self, mock_redis_backend):
        """
        Verify that OTPs expire exactly as defined by the Redis TTL parameters.
        Simulates a 301-second delay by explicitly removing/expiring the Redis key.
        """
        email = "ttl_expiry_test@beauty.com"

        # Generate OTP (cached in Redis with 300s TTL)
        otp = OTPService.generate_otp(email)

        client = mock_redis_backend
        key = f"otp:{email}"

        # Assert key initially exists with valid TTL
        assert client.exists(key) == 1
        assert 290 <= client.ttl(key) <= 300

        # Simulate 301-second delay by manually deleting the key (equivalent to TTL expiry)
        client.delete(key)

        # Attempt verification on expired token
        is_verified = OTPService.verify_otp(email, otp)
        assert is_verified is False

    # --------------------------------------------------------------------------
    # 2. REPLAY ATTACK PREVENTION TEST
    # --------------------------------------------------------------------------
    def test_otp_replay_attack_prevention(self):
        """
        Enforce absolute protection against token reuse.
        Attempting to verify the exact same correct OTP twice must fail on the second attempt.
        """
        email = "replay_attack_test@beauty.com"
        otp = OTPService.generate_otp(email)

        # Attempt 1: Successful verification
        assert OTPService.verify_otp(email, otp) is True

        # Attempt 2: Replay attack utilizing the same token must fail instantly
        assert OTPService.verify_otp(email, otp) is False

    @override_settings(EMAIL_PROVIDER="fake")
    @patch("users.tasks.send_mail")
    def test_fake_otp_dispatch_is_fast_and_non_networked(self, mocked_send_mail):
        assert send_express_otp_email.run("local@example.test", "123456") is True
        mocked_send_mail.assert_not_called()

    # --------------------------------------------------------------------------
    # 3. RATE LIMITING THROTTLING TEST
    # --------------------------------------------------------------------------
    def test_request_otp_throttling(self, api_client, client_ip):
        """
        Verify that AnonRateThrottle restricts request frequency to mitigate email toll fraud.
        Enforces strict response status code 429 when rate limits are breached.
        """
        email = "throttle_test@beauty.com"
        url = "/api/auth/request-otp/"

        # Clean rate limit caches for test isolation
        cache.clear()

        # Trigger 5 rapid requests (allowed within throttle boundaries)
        for _ in range(5):
            response = api_client.post(
                url,
                {"email": email, "turnstile_token": "CF_CLEARANCE_TEST_TOKEN"},
                REMOTE_ADDR=client_ip,
            )
            assert response.status_code == status.HTTP_200_OK

        # Trigger 6th request (violates rate limits)
        throttled_response = api_client.post(
            url,
            {"email": email, "turnstile_token": "CF_CLEARANCE_TEST_TOKEN"},
            REMOTE_ADDR=client_ip,
        )
        assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "detail" in throttled_response.data

    # --------------------------------------------------------------------------
    # 4. SOFT-DELETED USER INTERACTION TEST
    # --------------------------------------------------------------------------
    def test_otp_request_ignores_soft_deleted_users(self, api_client):
        """
        Ensure that soft-deleted/anonymized email accounts are completely blocked from auth operations.
        Any attempt to request or verify an OTP for a soft-deleted email must return a 400 Bad Request.
        """
        email = "soft_deleted_auth_test@beauty.com"
        user = User.objects.create_user(email=email)

        # Execute GDPR Anonymization (soft-delete)
        user.anonymize()

        # Attempt OTP Request
        request_url = "/api/auth/request-otp/"
        request_response = api_client.post(
            request_url,
            {"email": user.email, "turnstile_token": "CF_CLEARANCE_TEST_TOKEN"},
        )
        assert request_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in request_response.data
        assert "anonymized" in request_response.data["error"]

        # Attempt OTP Verification
        verify_url = "/api/auth/verify-otp/"
        verify_response = api_client.post(verify_url, {"email": user.email, "otp": "123456"})
        assert verify_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in verify_response.data
        assert "anonymized" in verify_response.data["error"]

    # --------------------------------------------------------------------------
    # 5. MALFORMED INPUTS & TURNSTILE TOKENS TEST
    # --------------------------------------------------------------------------
    def test_malformed_inputs_and_turnstile_failures(self, api_client):
        """
        Verify that missing payloads, malformed values, or rejected Turnstile clearing tokens
        are caught at the API perimeter and rejected with a 400 Bad Request.
        """
        # Test Case A: Missing Turnstile token in payload
        url = "/api/auth/request-otp/"
        response_missing_token = api_client.post(url, {"email": "malformed_test@beauty.com"})
        assert response_missing_token.status_code == status.HTTP_400_BAD_REQUEST
        assert "turnstile_token" in response_missing_token.data

        # Test Case B: Turnstile token challenge rejected by service check
        with patch("users.services.requests.post") as mock_post:
            # Simulate a Cloudflare rejection response
            mock_post.return_value.json.return_value = {
                "success": False,
                "error-codes": ["invalid-input-response"],
            }
            mock_post.return_value.status_code = 200

            response_rejected_token = api_client.post(
                url,
                {
                    "email": "turnstile_fail@beauty.com",
                    "turnstile_token": "INVALID_TOKEN",
                },
            )
            assert response_rejected_token.status_code == status.HTTP_400_BAD_REQUEST
            assert "error" in response_rejected_token.data
            assert "Bot challenge validation failed" in response_rejected_token.data["error"]
