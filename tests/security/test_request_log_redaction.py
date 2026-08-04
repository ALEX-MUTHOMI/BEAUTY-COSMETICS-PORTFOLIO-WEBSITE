import logging

from django.test import RequestFactory
from django.urls import resolve

from core.logging_filters import RequestPathRedactionFilter


def test_request_log_filter_uses_route_name_without_checkout_identifier():
    checkout_id = "11111111-1111-4111-8111-111111111111"
    request = RequestFactory().get(f"/api/checkout/sessions/{checkout_id}/")
    request.resolver_match = resolve(request.path)
    record = logging.getLogger("django.request").makeRecord(
        "django.request",
        logging.WARNING,
        __file__,
        0,
        "Too Many Requests: %s",
        (request.path,),
        None,
    )
    record.request = request
    record.status_code = 429

    assert RequestPathRedactionFilter().filter(record)
    assert record.getMessage() == "http_request status=429 route=checkout-session-detail"
    assert checkout_id not in record.getMessage()
