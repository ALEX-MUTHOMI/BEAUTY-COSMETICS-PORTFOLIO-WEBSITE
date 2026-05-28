from rest_framework.test import APIRequestFactory

from checkout.views import CheckoutMpesaWebhookView


def test_malformed_callback_response_is_generic():
    request = APIRequestFactory().post(
        "/api/checkout/mpesa/webhook/",
        {"CheckoutRequestID": "ws_CO_LEAK_TEST"},
        format="json",
        REMOTE_ADDR="127.0.0.1",
    )

    response = CheckoutMpesaWebhookView.as_view()(request)

    assert response.status_code == 400
    assert response.data == {"detail": "Malformed provider callback."}
    assert "ws_CO_LEAK_TEST" not in str(response.data)
