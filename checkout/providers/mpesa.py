import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from decimal import Decimal

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
from checkout.redaction import redact_checkout_payload


class MpesaProvider(BaseMpesaProvider):
    """
    Minimal bounded real-provider adapter.
    Default tests use FakeMpesaProvider; this adapter is only for opt-in paths.
    """

    def __init__(self, connect_timeout=None, read_timeout=None):
        self.connect_timeout = connect_timeout or getattr(settings, "MPESA_CONNECT_TIMEOUT", 2)
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
        return self._clean_env_like_value(key, value)

    def _clean_env_like_value(self, key, value):
        value = str(value).strip().strip("\"'")
        prefix = f"{key}="
        if value.startswith(prefix):
            value = value[len(prefix) :].strip().strip("\"'")
        return value

    def _validated_shortcode(self):
        shortcode = self._required_env("DARAJA_SHORTCODE")
        if not shortcode.isdigit():
            raise ProviderUnavailable("DARAJA_SHORTCODE must be numeric.")
        return shortcode

    def _validated_passkey(self):
        passkey = self._required_env("DARAJA_PASSKEY")
        if len(passkey) < 8:
            raise ProviderUnavailable("DARAJA_PASSKEY is invalid.")
        return passkey

    def _validated_callback_url(self, callback_url):
        callback_url = self._clean_env_like_value("DARAJA_CALLBACK_URL", callback_url)
        parsed = urllib.parse.urlparse(callback_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ProviderUnavailable("Daraja callback URL must be a valid HTTPS URL.")

        env_callback_url = self._clean_env_like_value("DARAJA_CALLBACK_URL", self._required_env("DARAJA_CALLBACK_URL"))
        env_host = urllib.parse.urlparse(env_callback_url).hostname
        if parsed.hostname != env_host:
            raise ProviderUnavailable("Daraja callback URL host does not match configured callback host.")
        return callback_url

    def _validated_amount(self, amount):
        try:
            normalized_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
        except Exception as exc:
            raise ProviderUnavailable("Daraja STK amount is invalid.") from exc
        if normalized_amount <= Decimal("0.00"):
            raise ProviderUnavailable("Daraja STK amount must be positive.")
        return int(normalized_amount)

    def _safe_error_diagnostic(self, exc):
        status_code = getattr(exc, "code", "unknown")
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        try:
            parsed_body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed_body = {"provider_error": body[:200]}
        redacted_body = redact_checkout_payload(parsed_body)
        redacted_body = self._redact_known_provider_secrets(redacted_body)
        safe_fields = {
            key: redacted_body.get(key)
            for key in (
                "errorCode",
                "errorMessage",
                "ResponseCode",
                "ResponseDescription",
                "CustomerMessage",
            )
            if key in redacted_body
        }
        return {"status_code": status_code, "body": safe_fields or {"provider_error": "redacted"}}

    def _redact_known_provider_secrets(self, value):
        secret_values = [
            os.environ.get(key, "")
            for key in (
                "DARAJA_CONSUMER_KEY",
                "DARAJA_CONSUMER_SECRET",
                "DARAJA_PASSKEY",
            )
            if os.environ.get(key)
        ]

        def redact(value):
            if isinstance(value, dict):
                return {key: redact(item) for key, item in value.items()}
            if isinstance(value, list):
                return [redact(item) for item in value]
            if not isinstance(value, str):
                return value
            for secret in secret_values:
                value = value.replace(secret, "redacted")
            return re.sub(r"password\s+[A-Za-z0-9+/=]{16,}", "password redacted", value, flags=re.IGNORECASE)

        return redact(value)

    def retrieve_oauth_token(self):
        self._require_https(self.oauth_endpoint)
        consumer_key = self._required_env("DARAJA_CONSUMER_KEY")
        consumer_secret = self._required_env("DARAJA_CONSUMER_SECRET")
        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
        request = urllib.request.Request(
            self.oauth_endpoint,
            headers={"Authorization": f"Basic {credentials}"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_budget) as response:  # nosec B310
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
        shortcode = self._validated_shortcode()
        passkey = self._validated_passkey()
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
        normalized_phone = normalize_mpesa_phone(phone_number)
        callback_url = self._validated_callback_url(callback_url)
        amount = self._validated_amount(amount)
        return {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
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
            with urllib.request.urlopen(request, timeout=self.timeout_budget) as response:  # nosec B310
                response_payload = json.loads(response.read().decode())
        except TimeoutError as exc:
            raise ProviderTimeout("M-Pesa STK request timed out.") from exc
        except urllib.error.HTTPError as exc:
            diagnostic = self._safe_error_diagnostic(exc)
            raise ProviderUnavailable(f"M-Pesa STK request failed safely: {diagnostic}") from exc
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise ProviderUnavailable("M-Pesa STK request failed safely.") from exc

        checkout_request_id = response_payload.get("CheckoutRequestID")
        merchant_request_id = response_payload.get("MerchantRequestID")
        if not checkout_request_id or not merchant_request_id:
            raise ProviderError("M-Pesa STK response did not include request identifiers.")
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
