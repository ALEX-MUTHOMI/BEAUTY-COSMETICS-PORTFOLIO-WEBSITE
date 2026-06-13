from __future__ import annotations

import copy
import re
from typing import Any

from django.conf import settings
from django.http import Http404, JsonResponse
from django.urls import URLPattern, URLResolver, get_resolver
from django.views.decorators.http import require_GET
from rest_framework.schemas.openapi import SchemaGenerator

ALLOWED_SCHEMA_PREFIXES = (
    "/health/",
    "/api/health-check/",
    "/api/csrf/",
    "/api/auth/",
    "/api/bookings/",
    "/api/checkout/",
    "/api/customers/",
    "/api/legal/",
    "/api/staff/",
    "/api/gallery/public/",
)

BANNED_SCHEMA_MARKERS = (
    "admin",
    "consumer_secret",
    "passkey",
    "access_token",
    "refresh_token",
    "sessionid",
    "receipt_token",
    "storage_key",
    "private_bucket",
    "raw_provider_payload",
    "checkout_id",
    "ledger_id",
    "provider_reference",
    "checkoutrequestid",
    "merchantrequestid",
    "mpesareceiptnumber",
)

SAFE_ROUTE_METHOD_BY_NAME = {
    "health-check": ("get",),
    "api-health-check": ("get",),
    "api-csrf-bootstrap": ("get",),
    "booking-catalog-services": ("get",),
    "booking-catalog-packages": ("get",),
    "booking-availability": ("get",),
    "booking-hold-create": ("post",),
    "booking-checkout-create": ("post",),
    "booking-policy-acceptance-text": ("get",),
    "booking-status": ("get",),
    "checkout-session-create": ("post",),
    "checkout-mpesa-webhook": ("post",),
    "request-otp": ("post",),
    "verify-otp": ("post",),
    "public-gallery-homepage": ("get",),
    "public-gallery-category": ("get",),
    "public-gallery-service": ("get",),
    "public-gallery-subcategory": ("get",),
}


def _flatten_patterns(patterns: list[URLPattern | URLResolver], prefix: str = "") -> list[URLPattern]:
    flattened: list[URLPattern] = []
    for pattern in patterns:
        route = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            flattened.extend(_flatten_patterns(pattern.url_patterns, route))
        elif route:
            flattened.append(pattern)
    return flattened


def _flatten_pattern_routes(
    patterns: list[URLPattern | URLResolver],
    prefix: str = "",
) -> list[tuple[str, URLPattern]]:
    flattened: list[tuple[str, URLPattern]] = []
    for pattern in patterns:
        route = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            flattened.extend(_flatten_pattern_routes(pattern.url_patterns, route))
        elif route:
            flattened.append((route, pattern))
    return flattened


def _to_openapi_path(route: str) -> str:
    route = route.replace("^", "").replace("$", "")
    converted = re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", route)
    if not converted.startswith("/"):
        converted = f"/{converted}"
    return converted


def _is_safe_schema_path(path: str) -> bool:
    lower_path = path.lower()
    if any(marker in lower_path for marker in BANNED_SCHEMA_MARKERS):
        return False
    return any(path.startswith(prefix) for prefix in ALLOWED_SCHEMA_PREFIXES)


def _redact_schema_markers(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_schema_markers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_schema_markers(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for marker in BANNED_SCHEMA_MARKERS:
            redacted = redacted.replace(marker, "[redacted]")
            redacted = redacted.replace(marker.upper(), "[redacted]")
            redacted = redacted.replace(marker.title(), "[redacted]")
        return redacted
    return value


def _route_inventory_operations(pattern: URLPattern) -> dict[str, Any]:
    methods = SAFE_ROUTE_METHOD_BY_NAME.get(pattern.name or "")
    if not methods:
        return {}
    return {
        method: {
            "operationId": f"{method}_{pattern.name}".replace("-", "_"),
            "summary": "Safe API contract route",
            "responses": {
                "200": {"description": "OK"},
                "201": {"description": "Created"},
                "202": {"description": "Accepted"},
                "400": {"description": "Bad request"},
                "401": {"description": "Unauthorized"},
                "403": {"description": "Forbidden"},
                "404": {"description": "Not found"},
                "429": {"description": "Rate limited"},
            },
        }
        for method in methods
    }


def _safe_route_inventory_paths() -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for route, pattern in _flatten_pattern_routes(get_resolver().url_patterns):
        path = _to_openapi_path(route)
        operations = _route_inventory_operations(pattern)
        if operations and _is_safe_schema_path(path):
            paths[path] = operations
    return paths


def build_safe_openapi_schema() -> dict[str, Any]:
    generator = SchemaGenerator(title="Beauty API", patterns=_flatten_patterns(get_resolver().url_patterns))
    schema = copy.deepcopy(generator.get_schema(request=None, public=True))
    paths = schema.get("paths", {})
    schema["paths"] = {
        path: _redact_schema_markers(path_schema) for path, path_schema in paths.items() if _is_safe_schema_path(path)
    }
    schema["paths"].update(
        {path: ops for path, ops in _safe_route_inventory_paths().items() if path not in schema["paths"]}
    )
    schema["info"] = {
        "title": "Beauty API",
        "version": "security-scan",
        "description": "Sanitized API schema for passive security scanning and contract verification.",
    }
    return _redact_schema_markers(schema)


@require_GET
def openapi_schema_view(_request):
    if not settings.ENABLE_OPENAPI_SCHEMA:
        raise Http404
    response = JsonResponse(build_safe_openapi_schema())
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
