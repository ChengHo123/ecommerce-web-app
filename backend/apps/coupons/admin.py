from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ("code", "discount_type", "value_display", "min_amount", "used_count", "usage_limit", "is_active", "expires_at")
    list_editable = ("is_active",)
    search_fields = ("code",)
    list_filter = ("discount_type", "is_active")
    readonly_fields = ("used_count", "created_at", "updated_at")
    list_per_page = 30

    @display(description="折扣")
    def value_display(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENT:
            return f"{obj.value}%"
        return f"${obj.value:,.0f}"

    @display(description="啟用", boolean=True)
    def active_badge(self, obj):
        return obj.is_active


@admin.register(CouponUsage)
class CouponUsageAdmin(ModelAdmin):
    list_display = ("coupon", "user", "order", "created_at")
    list_filter = ("coupon",)
    search_fields = ("user__name", "coupon__code")
    readonly_fields = ("coupon", "user", "order", "created_at")
    list_per_page = 30
