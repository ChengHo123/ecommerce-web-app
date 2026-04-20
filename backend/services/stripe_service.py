import stripe
from django.conf import settings
from django.urls import reverse


def refund_stripe_payment(order) -> bool:
    """Refund a Stripe payment. Looks up Payment record for session/transaction ID."""
    from apps.payments.models import Payment
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        payment = Payment.objects.get(order=order, provider=Payment.Provider.STRIPE)
    except Payment.DoesNotExist:
        return False

    if not payment.transaction_id:
        return False

    try:
        # Retrieve the checkout session to get the payment intent
        session = stripe.checkout.Session.retrieve(payment.transaction_id)
        payment_intent_id = session.get("payment_intent")
        if not payment_intent_id:
            return False

        stripe.Refund.create(payment_intent=payment_intent_id)
        payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=["status"])
        return True
    except Exception:
        return False


def create_stripe_session(order, request) -> str | None:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        line_items = [
            {
                "price_data": {
                    "currency": "twd",
                    "product_data": {"name": item.product_name},
                    "unit_amount": int(item.unit_price * 100),
                },
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ]

        base = request.build_absolute_uri("/")[:-1]
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            metadata={"order_no": order.order_no},
            success_url=base + f"/payment/stripe/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=base + "/payment/stripe/cancel/",
        )
        request.session["stripe_order_id"] = order.id
        return session.url
    except Exception:
        return None
