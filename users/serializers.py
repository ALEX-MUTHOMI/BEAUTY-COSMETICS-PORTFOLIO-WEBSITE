import re

from rest_framework import serializers


class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer validating incoming OTP requests at the security perimeter.
    - Enforces standard email formats.
    - Mandates a Cloudflare Turnstile token to mitigate distributed bot abuse.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Primary user email address requesting credentials validation.",
    )
    turnstile_token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Cloudflare Turnstile client clearance response challenge token.",
    )


class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer validating OTP verification request payloads.
    - Enforces standard email formats.
    - Mandates a 6-digit cryptographic numeric OTP token.
    """

    email = serializers.EmailField(
        required=True,
        help_text="User email address attempting authentication validation.",
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="The 6-digit verification code sent via high-priority express lane email.",
    )

    def validate_otp(self, value):
        """
        Verify code consists exclusively of 6 numerical digits.
        """
        if not re.match(r"^\d{6}$", value):
            raise serializers.ValidationError(
                "OTP code must be a 6-digit numeric string."
            )
        return value
