from decimal import Decimal

from rest_framework import serializers


class CheckoutSessionCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    currency = serializers.CharField(max_length=3, default="KES")
    description = serializers.CharField(max_length=255)
    purchasable_type = serializers.CharField(max_length=64)
    purchasable_id = serializers.CharField(max_length=128)
    idempotency_key = serializers.CharField(max_length=128)


class STKInitiationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    idempotency_key = serializers.CharField(max_length=128)


class MpesaWebhookSerializer(serializers.Serializer):
    CheckoutRequestID = serializers.CharField(max_length=128)
    MerchantRequestID = serializers.CharField(max_length=128, required=False)
    ResultCode = serializers.IntegerField()
    Amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    MpesaReceiptNumber = serializers.CharField(max_length=64, required=False, allow_blank=True)
