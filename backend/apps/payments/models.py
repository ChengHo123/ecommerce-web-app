from django.db import models


class Payment(models.Model):
    class Provider(models.TextChoices):
        LINEPAY = "linepay", "LINE Pay"
        STRIPE = "stripe", "Stripe"

    class Status(models.TextChoices):
        PENDING = "pending", "待付款"
        COMPLETED = "completed", "已完成"
        FAILED = "failed", "失敗"
        REFUNDED = "refunded", "已退款"

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        verbose_name = "付款記錄"
        verbose_name_plural = "付款記錄"

    def __str__(self):
        return f"{self.order.order_no} - {self.provider} ({self.status})"


class Review(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        verbose_name = "評論"
        verbose_name_plural = "評論"
        unique_together = [("user", "product")]

    def __str__(self):
        return f"{self.user.name} → {self.product.name} ({self.rating}★)"
