from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.permissions import IsSafaricomIP
from billing.throttles import STKPushRateThrottle


class MpesaWebhookView(APIView):
    authentication_classes = []
    permission_classes = [IsSafaricomIP]

    def post(self, request, *args, **kwargs):
        return Response(
            {"detail": "Billing M-Pesa webhook is disabled. Use /api/checkout/mpesa/webhook/."},
            status=status.HTTP_410_GONE,
        )


class STKPushView(APIView):
    throttle_classes = [STKPushRateThrottle]

    def post(self, request, *args, **kwargs):
        return Response(
            {"detail": "Billing STK initiation is disabled. Use /api/checkout/sessions/{id}/mpesa/stk/."},
            status=status.HTTP_410_GONE,
        )
