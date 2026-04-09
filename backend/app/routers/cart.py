from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product, ProductVariant
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartResponse, CartItemResponse
from app.routers.deps import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


async def get_or_create_cart(user: User, db: AsyncSession) -> Cart:
    result = await db.execute(select(Cart).where(Cart.user_id == user.id))
    cart = result.scalar_one_or_none()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.flush()
    return cart


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart = await get_or_create_cart(current_user, db)
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = result.scalars().all()

    cart_items = []
    total = 0.0
    for item in items:
        product_result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = product_result.scalar_one_or_none()
        if not product:
            continue

        price = product.base_price
        if item.variant_id:
            variant_result = await db.execute(select(ProductVariant).where(ProductVariant.id == item.variant_id))
            variant = variant_result.scalar_one_or_none()
            if variant:
                price = variant.price

        subtotal = price * item.quantity
        total += subtotal
        cart_items.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            product_name=product.name,
            product_image=product.images[0] if product.images else None,
            unit_price=price,
            subtotal=subtotal,
        ))

    return CartResponse(id=cart.id, items=cart_items, total=total)


@router.post("/items")
async def add_to_cart(
    data: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart = await get_or_create_cart(current_user, db)

    # Check existing
    query = select(CartItem).where(
        CartItem.cart_id == cart.id,
        CartItem.product_id == data.product_id,
        CartItem.variant_id == data.variant_id,
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.quantity += data.quantity
    else:
        item = CartItem(cart_id=cart.id, **data.model_dump())
        db.add(item)

    await db.commit()
    return {"message": "Added to cart"}


@router.patch("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart = await get_or_create_cart(current_user, db)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if data.quantity <= 0:
        await db.delete(item)
    else:
        item.quantity = data.quantity

    await db.commit()
    return {"message": "Cart updated"}


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart = await get_or_create_cart(current_user, db)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    await db.delete(item)
    await db.commit()
    return {"message": "Item removed"}


@router.delete("")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart = await get_or_create_cart(current_user, db)
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = result.scalars().all()
    for item in items:
        await db.delete(item)
    await db.commit()
    return {"message": "Cart cleared"}
