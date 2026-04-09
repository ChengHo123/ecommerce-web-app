from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product, ProductVariant
from app.models.coupon import Coupon, CouponUsage
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.common import PaginatedResponse
from app.routers.deps import get_current_user, get_current_admin
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/orders", tags=["orders"])


def generate_order_no() -> str:
    return f"ORD{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


@router.get("/my", response_model=PaginatedResponse[OrderResponse])
async def my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(select(func.count(Order.id)).where(Order.user_id == current_user.id))
    total = total_result.scalar()

    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    orders = result.scalars().all()

    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/my/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get cart
    cart_result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = cart_result.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    items_result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    cart_items = items_result.scalars().all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Validate logistics data
    if data.logistics_type.value == "cvs" and not data.cvs_store_id:
        raise HTTPException(status_code=400, detail="CVS store required for convenience store delivery")
    if data.logistics_type.value == "home" and not data.shipping_address:
        raise HTTPException(status_code=400, detail="Shipping address required for home delivery")

    # Calculate total
    total = 0.0
    order_items = []
    for cart_item in cart_items:
        product_result = await db.execute(select(Product).where(Product.id == cart_item.product_id))
        product = product_result.scalar_one_or_none()
        if not product:
            continue

        price = product.base_price
        variant_name = None
        if cart_item.variant_id:
            variant_result = await db.execute(select(ProductVariant).where(ProductVariant.id == cart_item.variant_id))
            variant = variant_result.scalar_one_or_none()
            if variant:
                price = variant.price
                variant_name = variant.name

        total += price * cart_item.quantity
        order_items.append({
            "product_id": cart_item.product_id,
            "variant_id": cart_item.variant_id,
            "quantity": cart_item.quantity,
            "unit_price": price,
            "product_name": product.name,
            "variant_name": variant_name,
        })

    # Apply coupon
    discount_amount = 0.0
    coupon = None
    if data.coupon_code:
        coupon_result = await db.execute(select(Coupon).where(Coupon.code == data.coupon_code, Coupon.is_active == True))
        coupon = coupon_result.scalar_one_or_none()
        if coupon and total >= coupon.min_amount:
            if coupon.discount_type.value == "percent":
                discount_amount = total * (coupon.value / 100)
            else:
                discount_amount = min(coupon.value, total)

    final_total = total - discount_amount

    # Create order
    order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        total=final_total,
        discount_amount=discount_amount,
        payment_method=data.payment_method,
        logistics_type=data.logistics_type,
        shipping_address=data.shipping_address.model_dump() if data.shipping_address else None,
        cvs_store_id=data.cvs_store_id,
        cvs_store_name=data.cvs_store_name,
        cvs_type=data.cvs_type,
        buyer_note=data.buyer_note,
        coupon_id=coupon.id if coupon else None,
    )
    db.add(order)
    await db.flush()

    for item_data in order_items:
        db.add(OrderItem(order_id=order.id, **item_data))

    if coupon:
        coupon.used_count += 1
        db.add(CouponUsage(coupon_id=coupon.id, user_id=current_user.id, order_id=order.id))

    # Clear cart
    for cart_item in cart_items:
        await db.delete(cart_item)

    await db.commit()
    await db.refresh(order)
    return order


# Admin endpoints
@router.get("", response_model=PaginatedResponse[OrderResponse], dependencies=[Depends(get_current_admin)])
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: OrderStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    orders = result.scalars().all()

    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.patch("/{order_id}/status", dependencies=[Depends(get_current_admin)])
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = new_status
    await db.commit()
    return {"message": "Order status updated"}
