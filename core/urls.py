"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from core.openapi import openapi_schema_view
from users.views import RequestOTPView, VerifyOTPView


def health_check(_request):
    return JsonResponse({"status": "ok"})


@ensure_csrf_cookie
@require_GET
def csrf_bootstrap(request):
    response = JsonResponse({"csrf_token": get_token(request)})
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("api/health-check/", health_check, name="api-health-check"),
    path("api/csrf/", csrf_bootstrap, name="api-csrf-bootstrap"),
    path("api/schema/", openapi_schema_view, name="api-openapi-schema"),
    path("api/auth/request-otp/", RequestOTPView.as_view(), name="request-otp"),
    path("api/auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("api/billing/", include("billing.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/checkout/", include("checkout.urls")),
    path("api/customers/", include("bookings.customer_urls")),
    path("api/legal/", include("bookings.legal_urls")),
    path("api/staff/", include("bookings.staff_urls")),
    path("api/gallery/public/", include("bookings.public_gallery_urls")),
]

if not settings.DISABLE_DJANGO_ADMIN:
    urlpatterns.append(path("admin/", admin.site.urls))
