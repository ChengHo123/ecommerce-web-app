from django.db import models
from django.conf import settings


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"
        verbose_name = "購物車"
        verbose_name_plural = "購物車"

    def __str__(self):
        return f"{self.user.name} 的購物車"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.select_related("variant", "product").all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_items")
    variant = models.ForeignKey(
        "products.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_items"
        verbose_name = "購物車項目"
        verbose_name_plural = "購物車項目"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.display_price
        return self.product.display_price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
