from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from checkout.exceptions import CheckoutValidationError
from checkout.permissions import IsSafaricomCheckoutIP
from checkout.providers.base import ProviderError
from checkout.providers.mpesa import MpesaProvider
from checkout.selectors import get_customer_checkout_or_none
from checkout.serializers import (
    CheckoutSessionCreateSerializer,
    MpesaWebhookSerializer,
    STKInitiationSerializer,
)
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)
from checkout.throttles import CheckoutSTKPushThrottle
from core.middleware.correlation_id import get_correlation_id


class CheckoutSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = create_checkout_session(
            customer=request.user,
            amount=serializer.validated_data["amount"],
            currency=serializer.validated_data["currency"],
            description=serializer.validated_data["description"],
            purchasable_type=serializer.validated_data["purchasable_type"],
            purchasable_id=serializer.validated_data["purchasable_id"],
            idempotency_key=serializer.validated_data["idempotency_key"],
        )
        return Response(
            {"id": str(session.id), "status": session.status},
            status=status.HTTP_201_CREATED,
        )


class CheckoutSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, checkout_id):
        session = get_customer_checkout_or_none(request.user, checkout_id)
        if session is None:
            raise Http404
        return Response(
            {
                "id": str(session.id),
                "status": session.status,
                "amount": str(session.amount_snapshot),
            }
        )


class CheckoutMpesaSTKView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CheckoutSTKPushThrottle]

    def post(self, request, checkout_id):
        session = get_customer_checkout_or_none(request.user, checkout_id)
        if session is None:
            raise Http404
        serializer = STKInitiationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            attempt = initiate_mpesa_stk(
                session.id,
                phone_number=serializer.validated_data["phone_number"],
                idempotency_key=serializer.validated_data["idempotency_key"],
            )
        except ProviderError:
            return Response(
                {"detail": "Payment provider temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"attempt_id": str(attempt.id), "status": attempt.status},
            status=status.HTTP_202_ACCEPTED,
        )


class CheckoutMpesaWebhookView(APIView):
    authentication_classes = []
    permission_classes = [IsSafaricomCheckoutIP]

    def post(self, request):
        try:
            payload = (
                MpesaProvider().normalize_callback(request.data)
                if isinstance(request.data, dict) and "Body" in request.data
                else request.data
            )
        except CheckoutValidationError:
            return Response(
                {"detail": "Malformed provider callback."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = MpesaWebhookSerializer(data=payload)
        if not serializer.is_valid():
            return Response(
                {"detail": "Malformed provider callback."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        process_mpesa_callback(
            dict(serializer.validated_data),
            request.META.get("REMOTE_ADDR"),
            get_correlation_id(),
        )
        return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)
