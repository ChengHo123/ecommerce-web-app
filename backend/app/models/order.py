from sqlalchemy import String, Numeric, Integer, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base
from app.models.mixins import TimestampMixin


class OrderStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class LogisticsType(str, enum.Enum):
    home = "home"       # 宅配
    cvs = "cvs"         # 超商取貨


class LogisticsStatus(str, enum.Enum):
    pending = "pending"
    created = "created"
    in_transit = "in_transit"
    arrived = "arrived"
    delivered = "delivered"
    failed = "failed"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.pending_payment)
    total: Mapped[float] = mapped_column(Numeric(10, 2))
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)  # linepay / stripe
    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.pending)

    # Logistics
    logistics_type: Mapped[LogisticsType | None] = mapped_column(SAEnum(LogisticsType), nullable=True)
    logistics_status: Mapped[LogisticsStatus] = mapped_column(SAEnum(LogisticsStatus), default=LogisticsStatus.pending)
    tracking_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipping_address: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cvs_store_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cvs_store_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cvs_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # UNIMART / FAMI

    # Notes
    buyer_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coupon_id: Mapped[int | None] = mapped_column(ForeignKey("coupons.id"), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="order", uselist=False)
    coupon: Mapped["Coupon | None"] = relationship("Coupon")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("product_variants.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    product_name: Mapped[str] = mapped_column(String(255))  # snapshot at order time
    variant_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    variant: Mapped["ProductVariant | None"] = relationship("ProductVariant", back_populates="order_items")
