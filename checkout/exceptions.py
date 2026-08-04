class CheckoutDomainError(Exception):
    pass


class CheckoutStateError(CheckoutDomainError):
    pass


class CheckoutValidationError(CheckoutDomainError):
    pass
