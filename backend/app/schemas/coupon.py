from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.coupon import DiscountType


class CouponCreate(BaseModel):
    code: str
    discount_type: DiscountType
    value: float
    min_amount: float = 0
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None


class CouponUpdate(BaseModel):
    value: Optional[float] = None
    min_amount: Optional[float] = None
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_type: DiscountType
    value: float
    min_amount: float
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None
    used_count: int
    is_active: bool

    model_config = {"from_attributes": True}


class CouponValidateRequest(BaseModel):
    code: str
    order_amount: float


class CouponValidateResponse(BaseModel):
    valid: bool
    discount_amount: float
    message: str
