import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentRecordStatus

stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_stripe_payment_intent(order) -> dict:
    """Create Stripe PaymentIntent for Apple Pay / credit card"""
    intent = stripe.PaymentIntent.create(
        amount=int(order.total * 100),  # Stripe uses cents
        currency="twd",
        metadata={"order_id": str(order.id), "order_no": order.order_no},
        payment_method_types=["card"],  # Apple Pay is served via card
        description=f"訂單 {order.order_no}",
    )
    return {"id": intent.id, "client_secret": intent.client_secret}


async def handle_stripe_webhook(event: dict, db: AsyncSession):
    """Handle Stripe webhook events"""
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_id = int(intent["metadata"].get("order_id", 0))

        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.payment_status = PaymentStatus.paid
            order.status = OrderStatus.paid

            payment_result = await db.execute(
                select(Payment).where(Payment.transaction_id == intent["id"])
            )
            payment = payment_result.scalar_one_or_none()
            if payment:
                payment.status = PaymentRecordStatus.completed

            await db.commit()

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        payment_result = await db.execute(
            select(Payment).where(Payment.transaction_id == intent["id"])
        )
        payment = payment_result.scalar_one_or_none()
        if payment:
            payment.status = PaymentRecordStatus.failed
            await db.commit()
