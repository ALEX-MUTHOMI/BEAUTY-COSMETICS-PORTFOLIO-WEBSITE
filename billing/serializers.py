from decimal import Decimal

from rest_framework import serializers


class MpesaWebhookSerializer(serializers.Serializer):
    checkout_request_id = serializers.CharField(max_length=128)
    result_code = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    mpesa_receipt_number = serializers.CharField(
        max_length=64, required=False, allow_blank=True
    )
    account_reference = serializers.EmailField(required=False)

    def validate(self, attrs):
        if attrs["result_code"] == 0:
            if "amount" not in attrs:
                raise serializers.ValidationError(
                    "Successful webhooks require an amount."
                )
            if attrs["amount"] <= Decimal("0.00"):
                raise serializers.ValidationError(
                    "Successful webhook amount must be positive."
                )
        return attrs


class STKPushSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("1.00")
    )
    checkout_request_id = serializers.CharField(max_length=128)
