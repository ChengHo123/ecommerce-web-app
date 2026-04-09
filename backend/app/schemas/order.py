from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus, PaymentStatus, LogisticsType, LogisticsStatus


class ShippingAddress(BaseModel):
    recipient_name: str
    phone: str
    postal_code: str
    city: str
    district: str
    address: str


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    unit_price: float
    product_name: str
    variant_name: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    logistics_type: LogisticsType
    payment_method: str  # linepay / stripe
    shipping_address: Optional[ShippingAddress] = None
    cvs_store_id: Optional[str] = None
    cvs_store_name: Optional[str] = None
    cvs_type: Optional[str] = None
    coupon_code: Optional[str] = None
    buyer_note: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_no: str
    status: OrderStatus
    total: float
    discount_amount: float
    payment_method: Optional[str] = None
    payment_status: PaymentStatus
    logistics_type: Optional[LogisticsType] = None
    logistics_status: LogisticsStatus
    tracking_no: Optional[str] = None
    shipping_address: Optional[dict] = None
    cvs_store_id: Optional[str] = None
    cvs_store_name: Optional[str] = None
    buyer_note: Optional[str] = None
    items: list[OrderItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
