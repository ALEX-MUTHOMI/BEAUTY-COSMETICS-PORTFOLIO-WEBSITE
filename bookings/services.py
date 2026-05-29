def create_booking_with_stk_push(user, service_date, time_slot, amount, checkout_request_id):
    """
    Deprecated Phase 2B bridge.

    Phase 2C-A intentionally routes payment orchestration through checkout using
    generic purchasable references. Booking must not create ledger transactions
    or initiate M-Pesa flows in this bounded context.
    """
    raise NotImplementedError("Booking payment bridge is disabled for Phase 2C-A. Use checkout sessions.")
