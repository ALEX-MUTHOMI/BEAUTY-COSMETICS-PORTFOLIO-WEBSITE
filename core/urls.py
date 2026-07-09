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
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from bookings import gallery_views
from core.openapi import openapi_schema_view
from core.throttling import route_throttle
from users.views import RequestOTPView, VerifyOTPView


def health_check(_request):
    """Shallow liveness — process is up (no dependency probes)."""
    return JsonResponse({"status": "ok"})


@require_GET
def readiness_check(_request):
    """
    Deep readiness — fail closed if Postgres or Redis is unreachable.
    Used by /api/health-check/; keep /health/ shallow for liveness.
    """
    from django.db import connection

    checks = {"database": "ok", "redis": "ok"}
    try:
        connection.ensure_connection()
    except Exception:
        checks["database"] = "error"
    try:
        from users.services import get_redis_client

        client = get_redis_client()
        if not client.ping():
            checks["redis"] = "error"
    except Exception:
        checks["redis"] = "error"

    ok = all(value == "ok" for value in checks.values())
    response = JsonResponse({"status": "ok" if ok else "degraded", "checks": checks}, status=200 if ok else 503)
    response["Cache-Control"] = "no-store"
    return response


@ensure_csrf_cookie
@require_GET
@route_throttle("csrf_bootstrap")
def csrf_bootstrap(request):
    response = JsonResponse({"csrf_token": get_token(request)})
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("api/health-check/", readiness_check, name="api-health-check"),
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
    re_path(
        r"^media/public/(?P<public_handle>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\.(?P<extension>webp|jpeg|jpg|png)$",
        gallery_views.public_gallery_variant,
        name="public-gallery-variant",
    ),
]

if not settings.DISABLE_DJANGO_ADMIN:
    urlpatterns.append(path("admin/", admin.site.urls))
