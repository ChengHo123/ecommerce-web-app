export interface User {
  id: number
  line_user_id: string | null
  email: string | null
  name: string
  phone: string | null
  avatar: string | null
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  parent_id: number | null
  sort_order: number
  children: Category[]
}

export interface ProductVariant {
  id: number
  name: string
  sku: string | null
  price: number
  stock: number
}

export interface Product {
  id: number
  name: string
  slug: string
  description: string | null
  base_price: number
  category_id: number | null
  status: 'active' | 'inactive' | 'out_of_stock'
  images: string[]
  stock: number
  has_variants: boolean
  variants: ProductVariant[]
  created_at: string
}

export interface CartItem {
  id: number
  product_id: number
  variant_id: number | null
  quantity: number
  product_name: string
  product_image: string | null
  unit_price: number
  subtotal: number
}

export interface Cart {
  id: number
  items: CartItem[]
  total: number
}

export interface ShippingAddress {
  recipient_name: string
  phone: string
  postal_code: string
  city: string
  district: string
  address: string
}

export interface OrderItem {
  id: number
  product_id: number
  variant_id: number | null
  quantity: number
  unit_price: number
  product_name: string
  variant_name: string | null
}

export interface Order {
  id: number
  order_no: string
  status: string
  total: number
  discount_amount: number
  payment_method: string | null
  payment_status: string
  logistics_type: string | null
  logistics_status: string
  tracking_no: string | null
  shipping_address: ShippingAddress | null
  cvs_store_id: string | null
  cvs_store_name: string | null
  buyer_note: string | null
  items: OrderItem[]
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
