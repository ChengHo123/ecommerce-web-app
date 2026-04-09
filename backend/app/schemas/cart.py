from pydantic import BaseModel
from typing import Optional
from app.schemas.product import ProductVariantResponse


class CartItemAdd(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    product_name: str
    product_image: Optional[str] = None
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse] = []
    total: float
