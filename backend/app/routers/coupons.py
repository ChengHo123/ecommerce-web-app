from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse, CouponValidateRequest, CouponValidateResponse
from app.routers.deps import get_current_admin

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(data: CouponValidateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(Coupon.code == data.code, Coupon.is_active == True))
    coupon = result.scalar_one_or_none()

    if not coupon:
        return CouponValidateResponse(valid=False, discount_amount=0, message="折扣碼不存在或已停用")

    if coupon.expires_at and coupon.expires_at < datetime.now(timezone.utc):
        return CouponValidateResponse(valid=False, discount_amount=0, message="折扣碼已過期")

    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return CouponValidateResponse(valid=False, discount_amount=0, message="折扣碼已達使用上限")

    if data.order_amount < coupon.min_amount:
        return CouponValidateResponse(
            valid=False,
            discount_amount=0,
            message=f"訂單金額需滿 NT${coupon.min_amount:.0f} 才可使用",
        )

    if coupon.discount_type.value == "percent":
        discount = data.order_amount * (coupon.value / 100)
    else:
        discount = min(coupon.value, data.order_amount)

    return CouponValidateResponse(valid=True, discount_amount=discount, message="折扣碼有效")


# Admin
@router.get("", response_model=list[CouponResponse], dependencies=[Depends(get_current_admin)])
async def list_coupons(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=CouponResponse, dependencies=[Depends(get_current_admin)])
async def create_coupon(data: CouponCreate, db: AsyncSession = Depends(get_db)):
    coupon = Coupon(**data.model_dump())
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return coupon


@router.patch("/{coupon_id}", response_model=CouponResponse, dependencies=[Depends(get_current_admin)])
async def update_coupon(coupon_id: int, data: CouponUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(coupon, field, value)
    await db.commit()
    await db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}", dependencies=[Depends(get_current_admin)])
async def delete_coupon(coupon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    await db.delete(coupon)
    await db.commit()
    return {"message": "Coupon deleted"}
