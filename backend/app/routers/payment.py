from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentProvider, PaymentRecordStatus
from app.models.user import User
from app.routers.deps import get_current_user
from app.services.line_pay import request_line_pay, confirm_line_pay
from app.services.stripe_service import create_stripe_payment_intent, handle_stripe_webhook
from app.core.config import settings
import stripe

router = APIRouter(prefix="/payment", tags=["payment"])


# ─── LINE Pay ───────────────────────────────────────────────────────────────

@router.post("/linepay/request")
async def linepay_request(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == current_user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Order already paid")

    response = await request_line_pay(order)
    if response.get("returnCode") != "0000":
        raise HTTPException(status_code=400, detail=f"LINE Pay error: {response.get('returnMessage')}")

    payment_url = response["info"]["paymentUrl"]["web"]
    transaction_id = str(response["info"]["transactionId"])

    # Save pending payment record
    payment = Payment(
        order_id=order.id,
        provider=PaymentProvider.linepay,
        transaction_id=transaction_id,
        amount=order.total,
        raw_response=response,
    )
    db.add(payment)
    await db.commit()

    return {"payment_url": payment_url, "transaction_id": transaction_id}


@router.get("/linepay/confirm")
async def linepay_confirm(
    transactionId: str,
    orderId: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Payment).where(Payment.transaction_id == transactionId))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalar_one_or_none()

    response = await confirm_line_pay(transactionId, order.total)
    if response.get("returnCode") != "0000":
        payment.status = PaymentRecordStatus.failed
        await db.commit()
        raise HTTPException(status_code=400, detail="LINE Pay confirmation failed")

    payment.status = PaymentRecordStatus.completed
    payment.raw_response = response
    order.payment_status = PaymentStatus.paid
    order.status = OrderStatus.paid
    await db.commit()

    return {"message": "Payment confirmed", "order_id": order.id}


# ─── Stripe / Apple Pay ──────────────────────────────────────────────────────

@router.post("/stripe/create-intent")
async def create_stripe_intent(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == current_user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Order already paid")

    intent = await create_stripe_payment_intent(order)

    payment = Payment(
        order_id=order.id,
        provider=PaymentProvider.stripe,
        transaction_id=intent["id"],
        amount=order.total,
    )
    db.add(payment)
    await db.commit()

    return {
        "client_secret": intent["client_secret"],
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    await handle_stripe_webhook(event, db)
    return {"status": "ok"}
