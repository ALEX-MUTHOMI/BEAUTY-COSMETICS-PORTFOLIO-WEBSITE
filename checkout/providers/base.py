from dataclasses import dataclass


class ProviderError(Exception):
    """Base error for bounded provider failures."""


class ProviderTimeout(ProviderError):
    """Provider did not respond inside the configured timeout budget."""


class ProviderUnavailable(ProviderError):
    """Provider is unavailable or not configured."""


@dataclass(frozen=True)
class MpesaProviderResponse:
    checkout_request_id: str
    merchant_request_id: str
    response_code: str = "0"
    response_description: str = "Accepted"


class BaseMpesaProvider:
    def initiate_stk_push(
        self,
        phone_number,
        amount,
        account_reference,
        description,
        callback_url,
        idempotency_key,
    ):
        raise NotImplementedError

    def parse_callback(self, payload):
        return dict(payload)

    def normalize_callback(self, payload):
        return dict(payload)

    def validate_provider_response(self, response):
        return response
