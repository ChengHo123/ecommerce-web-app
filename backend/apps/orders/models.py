from django.db import models
from django.conf import settings


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "待付款"
        PAID = "paid", "已付款"
        PROCESSING = "processing", "處理中"
        SHIPPED = "shipped", "已出貨"
        DELIVERED = "delivered", "已到貨"
        CANCELLED = "cancelled", "已取消"
        REFUNDED = "refunded", "已退款"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "待付款"
        PAID = "paid", "已付款"
        FAILED = "failed", "付款失敗"
        REFUNDED = "refunded", "已退款"

    class LogisticsType(models.TextChoices):
        HOME = "home", "宅配"
        CVS = "cvs", "超商取貨"

    class LogisticsStatus(models.TextChoices):
        PENDING = "pending", "待處理"
        CREATED = "created", "已建立"
        IN_TRANSIT = "in_transit", "運送中"
        ARRIVED = "arrived", "已到達"
        DELIVERED = "delivered", "已取貨"
        FAILED = "failed", "配送失敗"

    order_no = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_PAYMENT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    logistics_type = models.CharField(max_length=10, choices=LogisticsType.choices, null=True, blank=True)
    logistics_status = models.CharField(max_length=20, choices=LogisticsStatus.choices, default=LogisticsStatus.PENDING)
    tracking_no = models.CharField(max_length=100, null=True, blank=True)
    shipping_address = models.JSONField(null=True, blank=True)
    cvs_store_id = models.CharField(max_length=20, null=True, blank=True)
    cvs_store_name = models.CharField(max_length=100, null=True, blank=True)
    cvs_type = models.CharField(max_length=20, null=True, blank=True)
    buyer_note = models.CharField(max_length=500, null=True, blank=True)
    coupon = models.ForeignKey("coupons.Coupon", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        verbose_name = "訂單"
        verbose_name_plural = "訂單"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_no

    @property
    def subtotal(self):
        return self.total + self.discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="order_items")
    variant = models.ForeignKey(
        "products.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "order_items"
        verbose_name = "訂單項目"
        verbose_name_plural = "訂單項目"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
