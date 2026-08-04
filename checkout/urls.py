from django.urls import path

from checkout.views import (
    CheckoutMpesaSTKView,
    CheckoutMpesaWebhookView,
    CheckoutSessionDetailView,
    CheckoutSessionListCreateView,
)

urlpatterns = [
    path(
        "sessions/",
        CheckoutSessionListCreateView.as_view(),
        name="checkout-session-create",
    ),
    path(
        "sessions/<uuid:checkout_id>/",
        CheckoutSessionDetailView.as_view(),
        name="checkout-session-detail",
    ),
    path(
        "sessions/<uuid:checkout_id>/mpesa/stk/",
        CheckoutMpesaSTKView.as_view(),
        name="checkout-mpesa-stk",
    ),
    path(
        "mpesa/webhook/",
        CheckoutMpesaWebhookView.as_view(),
        name="checkout-mpesa-webhook",
    ),
]
