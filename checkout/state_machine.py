from checkout.exceptions import CheckoutStateError
from checkout.models import CheckoutSession

ALLOWED_TRANSITIONS = {
    CheckoutSession.Status.CREATED: {
        CheckoutSession.Status.CREATED,
        CheckoutSession.Status.PAYMENT_PENDING,
        CheckoutSession.Status.EXPIRED,
        CheckoutSession.Status.CANCELLED,
    },
    CheckoutSession.Status.PAYMENT_PENDING: {
        CheckoutSession.Status.PAYMENT_PENDING,
        CheckoutSession.Status.STK_SENT,
        CheckoutSession.Status.EXPIRED,
        CheckoutSession.Status.CANCELLED,
    },
    CheckoutSession.Status.STK_SENT: {
        CheckoutSession.Status.STK_SENT,
        CheckoutSession.Status.PAID,
        CheckoutSession.Status.FAILED,
        CheckoutSession.Status.EXPIRED,
        CheckoutSession.Status.CANCELLED,
    },
    CheckoutSession.Status.PAID: {CheckoutSession.Status.PAID},
    CheckoutSession.Status.FAILED: {CheckoutSession.Status.FAILED},
    CheckoutSession.Status.EXPIRED: {CheckoutSession.Status.EXPIRED},
    CheckoutSession.Status.CANCELLED: {CheckoutSession.Status.CANCELLED},
}


def transition_checkout(session, target_status):
    if target_status not in ALLOWED_TRANSITIONS[session.status]:
        raise CheckoutStateError(f"Illegal checkout transition {session.status} -> {target_status}.")
    session.status = target_status
    session.save(update_fields=["status", "updated_at"])
    return session
