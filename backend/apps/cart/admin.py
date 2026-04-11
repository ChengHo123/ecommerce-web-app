from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "variant", "quantity", "unit_price", "subtotal")

    def unit_price(self, obj):
        return obj.unit_price
    unit_price.short_description = "單價"

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "小計"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item_count", "total", "updated_at")
    search_fields = ("user__name", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]
