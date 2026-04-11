import stripe
from django.conf import settings
from django.urls import reverse


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
