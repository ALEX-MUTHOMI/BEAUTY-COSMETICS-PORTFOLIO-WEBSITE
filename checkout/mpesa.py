from decimal import Decimal

from checkout.exceptions import CheckoutValidationError


def normalize_mpesa_phone(phone_number):
    compact = str(phone_number).strip().replace(" ", "").replace("-", "")
    if compact.startswith("+"):
        compact = compact[1:]
    if compact.startswith("0"):
        compact = f"254{compact[1:]}"
    if len(compact) == 9 and compact.startswith(("7", "1")):
        compact = f"254{compact}"
    if not compact.startswith("254") or len(compact) != 12 or not compact.isdigit():
        raise CheckoutValidationError("Invalid Kenyan M-Pesa phone number.")
    return compact


def build_stk_push_payload(
    phone_number, amount, account_reference, description, callback_url
):
    normalized_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
    if normalized_amount <= Decimal("0.00"):
        raise CheckoutValidationError("STK amount must be positive.")
    return {
        "BusinessShortCode": "174379",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(int(normalized_amount)),
        "PartyA": normalize_mpesa_phone(phone_number),
        "PartyB": "174379",
        "PhoneNumber": normalize_mpesa_phone(phone_number),
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": description[:100],
    }
