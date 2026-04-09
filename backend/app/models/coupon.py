from sqlalchemy import String, Numeric, Integer, ForeignKey, Enum as SAEnum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from app.core.database import Base
from app.models.mixins import TimestampMixin


class DiscountType(str, enum.Enum):
    percent = "percent"
    fixed = "fixed"


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    discount_type: Mapped[DiscountType] = mapped_column(SAEnum(DiscountType))
    value: Mapped[float] = mapped_column(Numeric(10, 2))  # % or fixed amount
    min_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    usages: Mapped[list["CouponUsage"]] = relationship("CouponUsage", back_populates="coupon")


class CouponUsage(Base, TimestampMixin):
    __tablename__ = "coupon_usages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    coupon: Mapped["Coupon"] = relationship("Coupon", back_populates="usages")
    user: Mapped["User"] = relationship("User", back_populates="coupon_usages")
