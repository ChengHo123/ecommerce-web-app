from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.order import Order, OrderStatus, LogisticsStatus
from app.models.user import User
from app.routers.deps import get_current_user, get_current_admin
from app.services.ecpay_service import (
    create_cvs_shipment,
    create_home_shipment,
    get_ecpay_cvs_map_url,
)

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.get("/cvs-map-url")
async def get_cvs_map_url(cvs_type: str = "UNIMART"):
    """Get ECPay CVS store selection map URL (embed in frontend)"""
    url = get_ecpay_cvs_map_url(cvs_type)
    return {"url": url}


@router.post("/create-shipment/{order_id}", dependencies=[Depends(get_current_admin)])
async def create_shipment(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status.value != "paid":
        raise HTTPException(status_code=400, detail="Order not paid yet")

    if order.logistics_type.value == "cvs":
        tracking_no = await create_cvs_shipment(order)
    else:
        tracking_no = await create_home_shipment(order)

    order.tracking_no = tracking_no
    order.logistics_status = LogisticsStatus.created
    order.status = OrderStatus.shipped
    await db.commit()

    return {"message": "Shipment created", "tracking_no": tracking_no}


@router.post("/ecpay-callback")
async def ecpay_logistics_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """ECPay logistics status callback"""
    form_data = await request.form()
    merchant_trade_no = form_data.get("MerchantTradeNo")
    logistics_status = form_data.get("RtnCode")

    # MerchantTradeNo = order_no
    result = await db.execute(select(Order).where(Order.order_no == merchant_trade_no))
    order = result.scalar_one_or_none()
    if order and logistics_status == "300":  # 300 = delivered in ECPay
        order.logistics_status = LogisticsStatus.delivered
        order.status = OrderStatus.delivered
        await db.commit()

    return "1|OK"
