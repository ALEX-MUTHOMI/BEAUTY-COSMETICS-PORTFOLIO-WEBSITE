"""Score a very small set of post-response suspicious denials.

This middleware never inspects a request body, query string, storage key, or
response payload. It only runs Redis work for narrow 4xx abuse signals, so the
normal successful request path has no extra database or logging work.
"""

from __future__ import annotations

from core.abuse import record_abuse_signal


class AbuseSignalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # A raw/non-public media path is a common direct-storage enumeration
        # shape. The route itself is not logged or persisted.
        if (
            response.status_code == 404
            and request.path_info.startswith("/media/")
            and not request.path_info.startswith("/media/public/")
        ):
            record_abuse_signal(
                request,
                scope="media_resolver",
                event_type="RAW_STORAGE_PATH_ATTEMPT",
                points=4,
            )
        elif response.status_code == 403 and request.path_info.startswith("/api/checkout/mpesa/webhook/"):
            record_abuse_signal(
                request,
                scope="webhook",
                event_type="WEBHOOK_SOURCE_REJECTED",
                points=5,
            )
        return response
