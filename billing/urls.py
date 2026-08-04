from django.urls import path

from billing.views import MpesaWebhookView, STKPushView

urlpatterns = [
    path("mpesa-webhook/", MpesaWebhookView.as_view(), name="mpesa-webhook"),
    path("stk-push/", STKPushView.as_view(), name="stk-push"),
]
