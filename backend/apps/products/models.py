import uuid
from django.db import models


def _product_image_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"products/{instance.product_id}/{uuid.uuid4().hex[:12]}.{ext}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "分類"
        verbose_name_plural = "分類"
        ordering = ["sort_order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "上架"
        INACTIVE = "inactive", "下架"
        OUT_OF_STOCK = "out_of_stock", "缺貨"

    name = models.CharField(max_length=255)
    name_zh = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    summary_zh = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="products"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    images = models.JSONField(default=list)
    stock = models.IntegerField(default=0)
    unlimited_stock = models.BooleanField(default=False)
    has_variants = models.BooleanField(default=False)
    sku = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    mpn = models.CharField(max_length=100, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    tags = models.JSONField(default=list)
    promo_label = models.CharField(max_length=255, null=True, blank=True)
    promo_label_zh = models.CharField(max_length=255, null=True, blank=True)
    hide_price = models.BooleanField(default=False)
    is_preorder = models.BooleanField(default=False)
    preorder_note = models.TextField(null=True, blank=True)
    preorder_note_zh = models.TextField(null=True, blank=True)
    exclude_from_discount = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_title_zh = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_description_zh = models.TextField(null=True, blank=True)
    seo_keywords = models.CharField(max_length=500, null=True, blank=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    available_start = models.DateTimeField(null=True, blank=True)
    available_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name_zh or self.name

    @property
    def display_price(self):
        return self.sale_price if self.sale_price else self.base_price

    @property
    def first_image(self):
        # 優先用 ProductImage（ImageField，走 storage backend）
        img = self.product_images.order_by("order").first()
        if img:
            return img.image.url
        # 向下相容舊 JSONField 資料
        return next((url for url in self.images if url), None)

    @property
    def all_images(self):
        urls = [pi.image.url for pi in self.product_images.order_by("order")]
        if not urls:
            urls = [url for url in self.images if url]
        return urls

    @property
    def is_available(self):
        return self.status == self.Status.ACTIVE and (self.unlimited_stock or self.stock > 0)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to=_product_image_path)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "product_images"
        verbose_name = "商品圖片"
        verbose_name_plural = "商品圖片"
        ordering = ["order"]

    def __str__(self):
        return f"{self.product} 圖片 #{self.order}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)
    name_zh = models.CharField(max_length=100, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    mpn = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_variants"
        verbose_name = "商品規格"
        verbose_name_plural = "商品規格"

    def __str__(self):
        return f"{self.product} - {self.name_zh or self.name}"

    @property
    def display_price(self):
        return self.sale_price if self.sale_price else self.price
