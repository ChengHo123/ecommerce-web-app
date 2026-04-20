import logging
from django.db import models
from django.contrib import admin, messages
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Order, OrderItem

logger = logging.getLogger("apps.orders")


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
    actions = ["create_ecpay_shipment", "action_refund"]

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

    @admin.action(description="建立 ECPay 出貨單")
    def create_ecpay_shipment(self, request, queryset):
        from services.ecpay_logistics import create_shipment
        success = 0
        for order in queryset.filter(
            payment_status=Order.PaymentStatus.PAID,
            logistics_status__in=[Order.LogisticsStatus.PENDING, Order.LogisticsStatus.CREATED],
        ):
            callback_url = request.build_absolute_uri("/orders/logistics-callback/")
            result = create_shipment(order, server_reply_url=callback_url)
            if result["ok"]:
                order.logistics_status = Order.LogisticsStatus.CREATED
                order.status = Order.Status.PROCESSING
                order.tracking_no = result.get("trade_no", "")
                order.save(update_fields=["logistics_status", "status", "tracking_no"])
                success += 1
                logger.info("ECPay shipment created: order=%s trade_no=%s",
                            order.order_no, result.get("trade_no"))
            else:
                messages.warning(request, f"訂單 {order.order_no} 出貨失敗：{result['error']}")
                logger.error("ECPay shipment failed: order=%s error=%s",
                             order.order_no, result["error"])
        if success:
            messages.success(request, f"已成功建立 {success} 筆出貨單。")

    @admin.action(description="退款")
    def action_refund(self, request, queryset):
        success = 0
        for order in queryset.filter(payment_status=Order.PaymentStatus.PAID):
            refund_ok = False

            if order.payment_method == "linepay":
                from services.line_pay import refund_line_pay_payment
                try:
                    refund_ok = refund_line_pay_payment(order)
                except Exception:
                    logger.exception("LINE Pay refund failed: order=%s", order.order_no)

            elif order.payment_method == "stripe":
                from services.stripe_service import refund_stripe_payment
                try:
                    refund_ok = refund_stripe_payment(order)
                except Exception:
                    logger.exception("Stripe refund failed: order=%s", order.order_no)

            if refund_ok:
                order.payment_status = Order.PaymentStatus.REFUNDED
                order.status = Order.Status.REFUNDED
                order.save(update_fields=["payment_status", "status"])
                success += 1
                logger.info("Refund completed: order=%s method=%s",
                            order.order_no, order.payment_method)
            else:
                messages.warning(request, f"訂單 {order.order_no} 退款失敗。")

        # Restore stock for refunded orders
        for order in queryset.filter(status=Order.Status.REFUNDED):
            _restore_stock(order)

        if success:
            messages.success(request, f"已成功退款 {success} 筆訂單。")

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


def _restore_stock(order):
    """Restore product/variant stock when an order is refunded."""
    from apps.products.models import Product, ProductVariant
    for item in order.items.select_related("product", "variant").all():
        if item.variant:
            ProductVariant.objects.filter(pk=item.variant_id).update(
                stock=models.F("stock") + item.quantity,
            )
        elif item.product and not item.product.unlimited_stock:
            Product.objects.filter(pk=item.product_id).update(
                stock=models.F("stock") + item.quantity,
            )
