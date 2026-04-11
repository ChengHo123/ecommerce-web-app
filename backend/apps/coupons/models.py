from django.db import models
from django.conf import settings


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "折扣百分比"
        FIXED = "fixed", "固定金額"

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coupons"
        verbose_name = "優惠券"
        verbose_name_plural = "優惠券"

    def __str__(self):
        return self.code

    def calculate_discount(self, total: float) -> float:
        if self.discount_type == self.DiscountType.PERCENT:
            return float(total) * (float(self.value) / 100)
        return min(float(self.value), float(total))


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_usages")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupon_usages"
        verbose_name = "優惠券使用記錄"
        verbose_name_plural = "優惠券使用記錄"
