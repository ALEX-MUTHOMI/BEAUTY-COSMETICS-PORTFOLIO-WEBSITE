import time

from core.diagnostics import request_event


class RequestDiagnosticsMiddleware:
    """Logs a redacted request-completion event only when tracing is enabled."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.monotonic()
        response = self.get_response(request)
        request_event(request, response, int((time.monotonic() - started) * 1000))
        return response
