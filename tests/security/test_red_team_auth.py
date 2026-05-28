import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from core.celery import app as celery_app
from users.services import OTPService

User = get_user_model()


@pytest.fixture(autouse=True)
def eager_celery():
    """
    Force Celery to execute tasks synchronously in-memory during security testing
    so that dispatch logs and exceptions propagate directly to the assertion gates.
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
    return "198.51.100.42"  # Red Team simulated attacker IP


@pytest.mark.django_db
class TestRedTeamSecurityVerification:
    """
    Automated Red Team Penetration Testing Suite verifying identity perimeter
    security, rate-limiting defenses, and GDPR soft-deletion compliance.
    """

    # ==========================================================================
    # VECTOR A: Toll Fraud / SMS Pumping Attack
    # ==========================================================================
    def test_toll_fraud_sms_pumping_attack(self, api_client, client_ip):
        """
        Attack Scenario: Adversary attempts to flood the /request-otp/ endpoint
        15 times rapidly using automated scripts to pump SMS fees or toll costs.
        Defense: The system must enforce multi-factor OTPAnonRateThrottle (5/hour),
        blocking the injection and returning HTTP 429 Too Many Requests.
        """
        email = "toll_fraud_victim@beauty.com"
        url = "/api/auth/request-otp/"

        # Reset linter/throttle cache to ensure a clean state
        cache.clear()

        # Trigger rapid fire requests
        success_count = 0
        blocked_count = 0

        for _ in range(15):
            response = api_client.post(
                url,
                {"email": email, "turnstile_token": "CF_CLEARANCE_TEST_TOKEN"},
                REMOTE_ADDR=client_ip,
            )
            if response.status_code == status.HTTP_200_OK:
                success_count += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                blocked_count += 1

        # Assertions: first 5 are allowed (under 5/hour rate limit), next 10 are blocked
        assert success_count == 5
        assert blocked_count == 10
        assert success_count + blocked_count == 15

    # ==========================================================================
    # VECTOR B: OTP Replay Attack
    # ==========================================================================
    def test_otp_replay_attack(self, api_client):
        """
        Attack Scenario: Attacker intercepts a valid OTP token, completes validation,
        and immediately tries to verify the same code again to hijack/re-authenticate the session.
        Defense: The system must enforce Instant Key Destruction in Redis on first validation,
        meaning the second attempt must return HTTP 400 Bad Request.
        """
        email = "replay_target@beauty.com"

        # Generate a valid OTP through the secure service layer
        otp = OTPService.generate_otp(email)

        url = "/api/auth/verify-otp/"

        # Attempt 1: Valid authentication (must succeed)
        response_1 = api_client.post(url, {"email": email, "otp": otp})
        assert response_1.status_code == status.HTTP_200_OK
        assert response_1.data["email"] == email

        # Attempt 2: Replay attack with same token (must be blocked instantly)
        response_2 = api_client.post(url, {"email": email, "otp": otp})
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response_2.data
        assert "Invalid or expired" in response_2.data["error"]

    # ==========================================================================
    # VECTOR C: The Zombie Account Attack
    # ==========================================================================
    def test_zombie_account_attack(self, api_client):
        """
        Attack Scenario: Attacker attempts to target an anonymized/GDPR soft-deleted profile
        by guessing their scrambled email address to revive the user session ("Zombie Account").
        Defense: The system must enforce the soft-deletion security boundary. Requesting
        an OTP for an anonymized email must return HTTP 400 Bad Request to safely reject it.
        """
        original_email = "zombie_target@beauty.com"
        user = User.objects.create_user(email=original_email)

        # Anonymize/Soft-Delete the user under GDPR rules
        user.anonymize()
        user.refresh_from_db()

        # The scrambled email address currently registered on the deactivated record
        scrambled_email = user.email

        # Assert the email is indeed scrambled and marked deleted
        assert "anonymized-" in scrambled_email
        assert user.is_deleted is True

        # Attempt to request an OTP for the scrambled email address
        request_url = "/api/auth/request-otp/"
        response = api_client.post(
            request_url,
            {"email": scrambled_email, "turnstile_token": "CF_CLEARANCE_TEST_TOKEN"},
        )

        # The system must reject the request with HTTP 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "permanently deactivated" in response.data["error"]
