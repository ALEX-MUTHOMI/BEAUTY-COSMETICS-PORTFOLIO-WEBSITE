import logging
from django.contrib.auth import get_user_model, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import OTPRequestSerializer, OTPVerifySerializer
from users.throttles import OTPAnonRateThrottle
from users.services import OTPService
from users.tasks import send_express_otp_email

logger = logging.getLogger(__name__)
User = get_user_model()


class RequestOTPView(APIView):
    """
    API Perimeter: Request Passwordless OTP Verification Code.
    - Rate Throttling: Strictly enforced via Redis-backed OTPAnonRateThrottle.
    - Bot Mitigation: Mandates a validated Cloudflare Turnstile token.
    - Soft-Delete Protection: Blocks requests for deactivated/anonymized accounts.
    """
    throttle_classes = [OTPAnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].strip().lower()
        turnstile_token = serializer.validated_data["turnstile_token"]

        # 1. Validate Bot Challenge Perimeter
        ip_addr = request.META.get("REMOTE_ADDR")
        if not OTPService.verify_turnstile_token(turnstile_token, ip_addr):
            return Response(
                {"error": "Bot challenge validation failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Assert Soft-Deletion Boundary
        # If an account is soft-deleted/anonymized, we block OTP request immediately
        if User.objects.all_with_deleted().filter(email=email, is_deleted=True).exists():
            logger.warning(f"[-] Blocked OTP request attempt on soft-deleted account: {email}")
            return Response(
                {"error": "This account has been permanently deactivated/anonymized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Generate Cryptographic Code (Redis Express Lane)
        otp = OTPService.generate_otp(email)

        # 4. Dispatch Celery Task to High-Priority Queue
        send_express_otp_email.delay(email, otp)

        return Response(
            {"message": "Verification code dispatched successfully."},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    """
    API Perimeter: Validate OTP and Authenticate User.
    - Replay Attack Mitigation: Instantly destroys the token in Redis on validation.
    - Friction-free Onboarding: Auto-registers new users on verification.
    """
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].strip().lower()
        otp = serializer.validated_data["otp"]

        # 1. Assert Soft-Deletion Boundary
        if User.objects.all_with_deleted().filter(email=email, is_deleted=True).exists():
            return Response(
                {"error": "This account has been permanently deactivated/anonymized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Verify Cryptographic OTP against Redis
        if not OTPService.verify_otp(email, otp):
            return Response(
                {"error": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Onboard / Retrieve authenticated user
        user = User.objects.filter(email=email).first()
        is_new = False

        if not user:
            # Friction-free Onboarding: Auto-create account since OTP is verified
            user = User.objects.create_user(email=email)
            is_new = True
            logger.info(f"[+] Passwordless onboarding complete. Created new account: {email}")

        # 4. Bind session authentication context
        user.is_otp_verified = True
        user.save()
        
        login(request, user)
        logger.info(f"[+] Successful passwordless session login for: {email}")

        return Response(
            {
                "message": "Authentication successful.",
                "email": user.email,
                "is_new": is_new
            },
            status=status.HTTP_200_OK
        )
