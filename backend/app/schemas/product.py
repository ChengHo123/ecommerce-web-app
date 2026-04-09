from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.product import ProductStatus


class ProductVariantCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    price: float
    stock: int = 0


class ProductVariantResponse(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    price: float
    stock: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    base_price: float
    category_id: Optional[int] = None
    status: ProductStatus = ProductStatus.active
    images: list[str] = []
    stock: int = 0
    has_variants: bool = False
    variants: list[ProductVariantCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    category_id: Optional[int] = None
    status: Optional[ProductStatus] = None
    images: Optional[list[str]] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    base_price: float
    category_id: Optional[int] = None
    status: ProductStatus
    images: list
    stock: int
    has_variants: bool
    variants: list[ProductVariantResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
