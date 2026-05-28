import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

from django.conf import settings

from checkout.exceptions import CheckoutValidationError
from checkout.mpesa import normalize_mpesa_phone
from checkout.providers.base import (
    BaseMpesaProvider,
    MpesaProviderResponse,
    ProviderError,
    ProviderTimeout,
    ProviderUnavailable,
)


class MpesaProvider(BaseMpesaProvider):
    """
    Minimal bounded real-provider adapter.
    Default tests use FakeMpesaProvider; this adapter is only for opt-in paths.
    """

    def __init__(self, connect_timeout=None, read_timeout=None):
        self.connect_timeout = connect_timeout or getattr(
            settings, "MPESA_CONNECT_TIMEOUT", 2
        )
        self.read_timeout = read_timeout or getattr(settings, "MPESA_READ_TIMEOUT", 5)
        self.base_url = os.environ.get("DARAJA_BASE_URL", settings.DARAJA_BASE_URL)
        self.stk_endpoint = os.environ.get(
            "DARAJA_STK_URL",
            f"{self.base_url.rstrip('/')}/mpesa/stkpush/v1/processrequest",
        )
        self.oauth_endpoint = os.environ.get(
            "DARAJA_OAUTH_URL",
            f"{self.base_url.rstrip('/')}/oauth/v1/generate?grant_type=client_credentials",
        )

    @property
    def timeout_budget(self):
        return self.connect_timeout + self.read_timeout

    def _require_https(self, endpoint):
        if urllib.parse.urlparse(endpoint).scheme != "https":
            raise ProviderUnavailable("Daraja endpoint must use HTTPS.")

    def _required_env(self, key):
        value = os.environ.get(key)
        if not value:
            raise ProviderUnavailable(f"{key} is not configured.")
        return value

    def retrieve_oauth_token(self):
        self._require_https(self.oauth_endpoint)
        consumer_key = self._required_env("DARAJA_CONSUMER_KEY")
        consumer_secret = self._required_env("DARAJA_CONSUMER_SECRET")
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode()
        request = urllib.request.Request(
            self.oauth_endpoint,
            headers={"Authorization": f"Basic {credentials}"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_budget
            ) as response:  # nosec B310
                payload = json.loads(response.read().decode())
        except TimeoutError as exc:
            raise ProviderUnavailable("Daraja OAuth request timed out safely.") from exc
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as exc:
            raise ProviderUnavailable("Daraja OAuth request failed safely.") from exc

        token = payload.get("access_token")
        if not token:
            raise ProviderUnavailable("Daraja OAuth response did not contain a token.")
        return token

    def build_stk_push_payload(
        self,
        phone_number,
        amount,
        account_reference,
        description,
        callback_url,
    ):
        shortcode = self._required_env("DARAJA_SHORTCODE")
        passkey = self._required_env("DARAJA_PASSKEY")
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{shortcode}{passkey}{timestamp}".encode()
        ).decode()
        normalized_phone = normalize_mpesa_phone(phone_number)
        return {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": normalized_phone,
            "PartyB": shortcode,
            "PhoneNumber": normalized_phone,
            "CallBackURL": callback_url,
            "AccountReference": str(account_reference)[:12],
            "TransactionDesc": str(description)[:100],
        }

    def initiate_stk_push(
        self,
        phone_number,
        amount,
        account_reference,
        description,
        callback_url,
        idempotency_key,
    ):
        self._require_https(self.stk_endpoint)
        token = self.retrieve_oauth_token()

        payload = self.build_stk_push_payload(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            description=description,
            callback_url=callback_url,
        )
        request = urllib.request.Request(
            self.stk_endpoint,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_budget
            ) as response:  # nosec B310
                response_payload = json.loads(response.read().decode())
        except TimeoutError as exc:
            raise ProviderTimeout("M-Pesa STK request timed out.") from exc
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise ProviderUnavailable("M-Pesa STK request failed safely.") from exc

        checkout_request_id = response_payload.get("CheckoutRequestID")
        merchant_request_id = response_payload.get("MerchantRequestID")
        if not checkout_request_id or not merchant_request_id:
            raise ProviderError(
                "M-Pesa STK response did not include request identifiers."
            )
        return MpesaProviderResponse(
            checkout_request_id=checkout_request_id,
            merchant_request_id=merchant_request_id,
            response_code=str(response_payload.get("ResponseCode", "")),
            response_description=str(response_payload.get("ResponseDescription", "")),
        )

    def normalize_callback(self, payload):
        callback = (payload or {}).get("Body", {}).get("stkCallback")
        if not callback:
            raise CheckoutValidationError("Malformed provider callback.")

        normalized = {
            "CheckoutRequestID": str(callback.get("CheckoutRequestID", "")),
            "MerchantRequestID": str(callback.get("MerchantRequestID", "")),
            "ResultCode": int(callback.get("ResultCode", 1)),
        }
        metadata = callback.get("CallbackMetadata", {}).get("Item", [])
        for item in metadata:
            name = item.get("Name")
            if name == "Amount":
                normalized["Amount"] = f"{float(item.get('Value')):.2f}"
            elif name == "MpesaReceiptNumber":
                normalized["MpesaReceiptNumber"] = str(item.get("Value", ""))
            elif name == "TransactionDate":
                normalized["ProviderTimestamp"] = str(item.get("Value", ""))
            elif name == "PhoneNumber":
                normalized["PhoneNumber"] = str(item.get("Value", ""))
        normalized.setdefault("Amount", "0.00")
        normalized.setdefault("MpesaReceiptNumber", "")
        if not normalized["CheckoutRequestID"] or not normalized["MerchantRequestID"]:
            raise CheckoutValidationError("Malformed provider callback.")
        return normalized
