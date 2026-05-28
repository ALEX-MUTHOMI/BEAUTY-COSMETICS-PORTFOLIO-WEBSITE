from checkout.models import CheckoutSession


def get_customer_checkout_or_none(customer, checkout_id):
    return CheckoutSession.objects.filter(id=checkout_id, customer=customer).first()
