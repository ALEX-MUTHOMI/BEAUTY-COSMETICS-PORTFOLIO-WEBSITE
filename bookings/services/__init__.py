def create_booking_with_stk_push(user, service_date, time_slot, amount, checkout_request_id):
    """
    Deprecated bridge.

    Payment orchestration belongs to checkout/. Billing ledger truth belongs to
    billing/. Booking owns scheduling and must not initiate STK pushes.
    """
    raise NotImplementedError("Booking payment bridge is disabled. Use checkout sessions.")
