from django.urls import path

from bookings.customer_views import forget_remembered_device, remember_device, remembered_device, use_remembered_device

urlpatterns = [
    path("remember-device/", remember_device, name="customer-remember-device"),
    path("remembered-device/", remembered_device, name="customer-remembered-device"),
    path("remembered-device/use/", use_remembered_device, name="customer-use-remembered-device"),
    path("remembered-device/forget/", forget_remembered_device, name="customer-forget-remembered-device"),
]
