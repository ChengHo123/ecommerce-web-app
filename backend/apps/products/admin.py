import logging
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Category, Product, ProductImage, ProductVariant

logger = logging.getLogger("apps.products")


class ProductAdminForm(forms.ModelForm):
    """
    unfold 的 tab 用 x-if 把非 active tab 從 DOM 移除，
    導致隱藏 tab 的 JSONField 沒被送出 → required 驗證失敗。
    把這些欄位設為 not required，並在 clean 時補回原始值。
    """
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("tags", "images"):
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_tags(self):
        v = self.cleaned_data.get("tags")
        if v is None:
            return self.instance.tags if self.instance.pk else []
        return v

    def clean_images(self):
        v = self.cleaned_data.get("images")
        if v is None:
            return self.instance.images if self.instance.pk else []
        return v


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "parent", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 30


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ("preview", "image", "alt_text", "order")
    readonly_fields = ("preview",)
    tab = True

    @display(description="預覽")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:64px;width:64px;object-fit:cover;border-radius:4px;">',
                obj.image.url,
            )
        return "—"


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("name", "name_zh", "sku", "price", "sale_price", "stock", "weight")
    tab = True


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "show_name", "status_badge", "base_price", "sale_price",
        "stock_display", "category", "created_at",
    )
    list_filter = ("status", "category", "has_variants", "is_preorder", "unlimited_stock")
    search_fields = ("name", "name_zh", "sku", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("基本資訊", {
            "fields": ("name", "name_zh", "slug", "category", "status"),
        }),
        ("描述", {
            "fields": ("summary", "summary_zh", "description"),
            "classes": ["tab"],
        }),
        ("價格與庫存", {
            "fields": ("base_price", "sale_price", "cost", "stock", "unlimited_stock", "has_variants"),
            "classes": ["tab"],
        }),
        ("商品資訊", {
            "fields": ("sku", "barcode", "mpn", "weight", "brand", "tags"),
            "classes": ["tab"],
        }),
        ("促銷", {
            "fields": ("promo_label", "promo_label_zh", "hide_price", "exclude_from_discount"),
            "classes": ["tab"],
        }),
        ("預購", {
            "fields": ("is_preorder", "preorder_note", "preorder_note_zh"),
            "classes": ["tab"],
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_title_zh", "seo_description", "seo_description_zh", "seo_keywords"),
            "classes": ["tab"],
        }),
        ("排程", {
            "fields": ("publish_at", "available_start", "available_end"),
            "classes": ["tab"],
        }),
        ("時間", {
            "fields": ("created_at", "updated_at"),
            "classes": ["tab"],
        }),
    )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST":
            resp = super().changeform_view(request, object_id, form_url, extra_context)
            if getattr(resp, "status_code", None) == 200:
                obj = self.get_object(request, object_id)
                form = self.get_form(request)(request.POST, request.FILES, instance=obj)
                if not form.is_valid():
                    logger.warning("form errors pk=%s: %s", object_id, dict(form.errors))
                for inline in self.get_inline_instances(request):
                    fs = inline.get_formset(request)(request.POST, request.FILES, instance=obj)
                    if not fs.is_valid():
                        logger.warning("inline %s errors: %s", inline.__class__.__name__, fs.errors)
            return resp
        return super().changeform_view(request, object_id, form_url, extra_context)

    @display(description="商品名稱")
    def show_name(self, obj):
        return obj.name_zh or obj.name

    @display(description="狀態", label={
        "active": "success",
        "inactive": "danger",
        "out_of_stock": "warning",
    })
    def status_badge(self, obj):
        return obj.status

    @display(description="庫存")
    def stock_display(self, obj):
        if obj.unlimited_stock:
            return "無限"
        return obj.stock
