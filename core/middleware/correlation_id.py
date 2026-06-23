import logging
import uuid
from contextvars import ContextVar

correlation_id_var = ContextVar("correlation_id", default=None)


def get_correlation_id():
    return correlation_id_var.get()


def set_correlation_id(value=None):
    correlation_id = value or str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = get_correlation_id() or "-"
        return True


class CorrelationIdMiddleware:
    """
    Assigns a stable request correlation ID across Django logging, responses,
    and Celery task dispatch performed during the request lifecycle.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # A client-controlled request ID must never enter logs, task metadata,
        # or a response header. Generate a server-side value for every request.
        request_id = set_correlation_id()
        request.correlation_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
