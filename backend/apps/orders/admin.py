from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "product_name", "variant_name", "quantity", "unit_price", "item_subtotal")
    tab = True

    @display(description="小計")
    def item_subtotal(self, obj):
        return f"${obj.subtotal:,.0f}"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "order_no", "user", "status_badge", "payment_badge",
        "total_display", "logistics_type", "created_at",
    )
    list_filter = ("status", "payment_status", "logistics_type", "payment_method")
    search_fields = ("order_no", "user__name", "user__email")
    readonly_fields = ("order_no", "created_at", "updated_at")
    inlines = [OrderItemInline]
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("訂單資訊", {
            "fields": ("order_no", "user", "status", "buyer_note"),
        }),
        ("付款", {
            "fields": ("payment_method", "payment_status", "total", "discount_amount", "coupon"),
            "classes": ["tab"],
        }),
        ("物流", {
            "fields": ("logistics_type", "logistics_status", "tracking_no", "shipping_address",
                       "cvs_store_id", "cvs_store_name", "cvs_type"),
            "classes": ["tab"],
        }),
        ("時間", {
            "fields": ("created_at", "updated_at"),
            "classes": ["tab"],
        }),
    )

    @display(description="訂單狀態", label={
        "pending_payment": "warning",
        "paid": "info",
        "processing": "info",
        "shipped": "success",
        "delivered": "success",
        "cancelled": "danger",
        "refunded": "danger",
    })
    def status_badge(self, obj):
        return obj.status

    @display(description="付款狀態", label={
        "pending": "warning",
        "paid": "success",
        "failed": "danger",
        "refunded": "danger",
    })
    def payment_badge(self, obj):
        return obj.payment_status

    @display(description="金額")
    def total_display(self, obj):
        return f"${obj.total:,.0f}"
