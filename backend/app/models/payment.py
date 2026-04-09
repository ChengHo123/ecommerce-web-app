from sqlalchemy import String, Numeric, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base
from app.models.mixins import TimestampMixin


class PaymentProvider(str, enum.Enum):
    linepay = "linepay"
    stripe = "stripe"


class PaymentRecordStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    provider: Mapped[PaymentProvider] = mapped_column(SAEnum(PaymentProvider))
    transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[PaymentRecordStatus] = mapped_column(SAEnum(PaymentRecordStatus), default=PaymentRecordStatus.pending)
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="payment")
