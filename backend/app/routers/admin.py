from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.product import Product
from app.models.user import User
from app.routers.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Today revenue
    today_revenue_result = await db.execute(
        select(func.sum(Order.total)).where(
            Order.payment_status == PaymentStatus.paid,
            Order.created_at >= today_start,
        )
    )
    today_revenue = today_revenue_result.scalar() or 0

    # Month revenue
    month_revenue_result = await db.execute(
        select(func.sum(Order.total)).where(
            Order.payment_status == PaymentStatus.paid,
            Order.created_at >= month_start,
        )
    )
    month_revenue = month_revenue_result.scalar() or 0

    # Total orders today
    today_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today_start)
    )
    today_orders = today_orders_result.scalar() or 0

    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.paid)
    )
    pending_orders = pending_result.scalar() or 0

    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    # Low stock products (stock < 10)
    low_stock_result = await db.execute(
        select(func.count(Product.id)).where(Product.stock < 10, Product.has_variants == False)
    )
    low_stock = low_stock_result.scalar() or 0

    # Monthly revenue for last 6 months
    monthly_data = []
    for i in range(5, -1, -1):
        start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
        rev_result = await db.execute(
            select(func.sum(Order.total)).where(
                Order.payment_status == PaymentStatus.paid,
                Order.created_at >= start,
                Order.created_at < end,
            )
        )
        monthly_data.append({
            "month": start.strftime("%Y-%m"),
            "revenue": float(rev_result.scalar() or 0),
        })

    return {
        "today_revenue": float(today_revenue),
        "month_revenue": float(month_revenue),
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "total_users": total_users,
        "low_stock_count": low_stock,
        "monthly_revenue": monthly_data,
    }
