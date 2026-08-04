class BillingDomainError(Exception):
    pass


class BillingInvariantError(BillingDomainError):
    pass


class BillingStateError(BillingDomainError):
    pass
