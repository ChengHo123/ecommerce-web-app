from django.contrib import admin
from .models import Payment, Review


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "transaction_id", "amount", "status", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("order__order_no", "transaction_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("user__name", "product__name")
    readonly_fields = ("created_at",)
