"""Safe, uniform API error rendering for admission-control failures."""

from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler as drf_exception_handler

from core.throttling import ThrottleInfrastructureUnavailable


def api_exception_handler(exc, context):
    """Keep throttle response bodies generic while preserving Retry-After."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, Throttled):
        response.data = {"detail": "Too many requests. Please try again later."}
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
    elif isinstance(exc, ThrottleInfrastructureUnavailable):
        response.data = {"detail": "Service temporarily unavailable."}
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
    return response
