import io
import logging
import re
import openpyxl
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin, messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, ProductVariant, Category

logger = logging.getLogger("apps.products")

# ── Shopline special string constants ───────────────────────────────────────
_UNLIMITED = '\u7121\u9650\u6578\u91cf'   # 無限數量
_SAME_PRICE = '\u50f9\u683c\u4e00\u81f4'  # 價格一致


def home(request):
    featured = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")[:8]
    categories = Category.objects.filter(parent=None)
    return render(request, "home.html", {"featured": featured, "categories": categories})


def product_list(request):
    qs = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")

    category_slug = request.GET.get("category")
    search = request.GET.get("q", "").strip()
    selected_category = None

    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            qs = qs.filter(category=selected_category)

    if search:
        qs = qs.filter(name__icontains=search) | Product.objects.filter(
            name_zh__icontains=search, status=Product.Status.ACTIVE
        )
        qs = qs.distinct()

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))

    categories = Category.objects.filter(parent=None)
    return render(request, "products/list.html", {
        "page": page,
        "categories": categories,
        "selected_category": selected_category,
        "search": search,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("variants"),
        slug=slug,
        status=Product.Status.ACTIVE,
    )
    reviews = product.reviews.select_related("user").order_by("-created_at")[:10]
    return render(request, "products/detail.html", {
        "product": product,
        "reviews": reviews,
    })


# ── Admin bulk import ────────────────────────────────────────────────────────

# Shopline column index map (0-based)
_COL = {
    "shopline_id": 0,
    "name_en": 1,       "name_zh": 2,
    "summary_en": 3,    "summary_zh": 4,
    "seo_title_en": 5,  "seo_title_zh": 6,
    "seo_desc_en": 7,   "seo_desc_zh": 8,
    "seo_keywords": 9,
    "hidden": 10,       "preorder": 11,
    "preorder_note_en": 12, "preorder_note_zh": 13,
    "status": 14,
    "publish_at": 15,   "avail_start": 16, "avail_end": 17,
    "brand": 18,        "hide_price": 19,
    "categories": 20,
    "base_price": 21,   "sale_price": 22,
    # 23-26: member/wholesale prices → skip
    "unlimited_qty": 27,
    # 28: same_price flag
    "cost": 29,         "sku": 30,
    "quantity": 31,
    # 32: update_quantity delta → skip
    "weight": 33,       "tags": 34,
    "promo_label_en": 35, "promo_label_zh": 36,
    # 37-38: excluded payment/delivery → skip
    # 39: variant id → skip
    "var_name_en": 40,  "var_name_zh": 41,
    "var_qty": 42,
    # 43: update_var_qty delta → skip
    "var_price": 44,    "var_sale_price": 45,
    # 46-49: variant member/wholesale prices → skip
    "var_cost": 50,     "var_weight": 51,
    "var_sku": 52,
    # 53: location id → skip
    "mpn": 54,          "barcode": 55,
    # 56-57: SL_STOCK_ID, Warehouse → skip
    "exclude_discount": 58,
    # 59-60: SL_KEY0, SL_KEY1 → skip
}


def _col(row, key):
    idx = _COL.get(key)
    if idx is None or idx >= len(row):
        return None
    v = row[idx]
    return v if v != "" else None


def _slugify(text: str) -> str:
    """ASCII-only slug. Non-ASCII chars (e.g. Chinese) are stripped."""
    text = text.lower().strip()
    text = re.sub(r"[^\x00-\x7f]", "", text)   # strip non-ASCII (Chinese etc.)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or ""


def _parse_bool(val) -> bool:
    if val is None:
        return False
    return str(val).strip().upper() in ("Y", "YES", "TRUE", "1")


def _parse_qty(val) -> tuple[int, bool]:
    """Return (stock, unlimited_stock). Handles '無限數量' and negatives."""
    if val is None or val == "":
        return 0, False
    s = str(val).strip()
    if s == _UNLIMITED:
        return 0, True
    try:
        n = int(float(s))
        return max(n, 0), False
    except (ValueError, TypeError):
        return 0, False


def _parse_price(val, fallback=0) -> float | None:
    """Return float price. 0.0 → None (no sale price). '價格一致' → fallback."""
    if val is None or val == "":
        return None
    s = str(val).strip()
    if s == _SAME_PRICE:
        return float(fallback) if fallback else None
    try:
        f = float(s)
        return f if f > 0 else None
    except (ValueError, TypeError):
        return None


def _parse_str(val) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s or None


def _get_or_create_category(name: str, parent: "Category | None" = None) -> "Category | None":
    """Find or create a category by name. Returns None if name is empty."""
    name = name.strip()
    if not name:
        return None
    slug = _slugify(name) or name.lower()  # fallback to name for non-ASCII (e.g. Chinese)
    cat, _ = Category.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "parent": parent},
    )
    return cat


def _build_category_hierarchy(cats_raw: str) -> "Category | None":
    """
    Parse a newline-separated Shopline category string and build parent-child
    relationships.  Shopline lists categories from most-specific → most-general,
    e.g. "兔兔飼料\n全部商品\n首頁" means 首頁 > 全部商品 > 兔兔飼料.
    Returns the most-specific (leaf) category.
    """
    _SKIP = {"Featured Products", "首頁"}
    cat_list = [c.strip() for c in str(cats_raw).split("\n") if c.strip()]
    filtered = [c for c in cat_list if c and not c.startswith("SL_") and c not in _SKIP]
    if not filtered:
        return None

    # Shopline order: [leaf, ..., root] → reverse to build top-down
    ordered = list(reversed(filtered))

    parent = None
    leaf = None
    for name in ordered:
        leaf = _get_or_create_category(name, parent=parent)
        parent = leaf
    return leaf


def _unique_slug(base: str) -> str:
    slug = base
    counter = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


@staff_member_required
def bulk_import(request):
    if request.method == "GET":
        context = {
            **admin.site.each_context(request),
            "title": "批量匯入商品",
        }
        return render(request, "admin/products/bulk_import.html", context)

    uploaded = request.FILES.get("file")
    if not uploaded or not uploaded.name.endswith((".xlsx", ".xls")):
        messages.error(request, "只接受 .xlsx / .xls 檔案")
        return redirect("bulk_import")

    try:
        wb = openpyxl.load_workbook(io.BytesIO(uploaded.read()), data_only=True)
    except Exception:
        messages.error(request, "無法解析 Excel 檔案")
        return redirect("bulk_import")

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 3:
        messages.error(request, "Excel 資料不足（需要至少 3 列）")
        return redirect("bulk_import")

    created = updated = skipped = 0
    errors = []

    current_data: dict | None = None
    current_variants: list[dict] = []
    current_base_price: float = 0

    def flush_product():
        nonlocal created, updated, current_data, current_variants
        if not current_data:
            return

        name = current_data.get("name") or current_data.get("name_zh") or ""
        if not name:
            return

        # Match priority: SKU → name_zh → name
        existing = None
        if current_data.get("sku"):
            existing = Product.objects.filter(sku=current_data["sku"]).first()
        if not existing and current_data.get("name_zh"):
            existing = Product.objects.filter(name_zh=current_data["name_zh"]).first()
        if not existing:
            existing = Product.objects.filter(name=name).first()

        current_data["has_variants"] = len(current_variants) > 0

        if existing:
            for k, v in current_data.items():
                if v is not None:
                    setattr(existing, k, v)
            existing.save()
            existing.variants.all().delete()
            for vd in current_variants:
                ProductVariant.objects.create(product=existing, **vd)
            updated += 1
        else:
            # Try name_en first (ASCII-friendly), fall back to SKU, then numeric id
            slug_base = (
                _slugify(current_data.get("name") or "")
                or _slugify(current_data.get("sku") or "")
                or f"product-{Product.objects.count() + 1}"
            )
            slug = _unique_slug(slug_base)
            p = Product.objects.create(slug=slug, **{k: v for k, v in current_data.items() if v is not None})
            for vd in current_variants:
                ProductVariant.objects.create(product=p, **vd)
            created += 1

        current_data = None
        current_variants.clear()

    for row_num, row in enumerate(rows[2:], start=3):
        name_en = _col(row, "name_en")
        name_zh = _col(row, "name_zh")

        # ── Product row (has name) ───────────────────────────────────────
        if name_en or name_zh:
            try:
                flush_product()
            except Exception as e:
                errors.append(f"第 {row_num - 1} 行: {e}")
                logger.error("bulk_import flush error at row %d: %s", row_num - 1, e, exc_info=True)

            name = str(name_en).strip() if name_en else str(name_zh).strip()

            hidden = _parse_bool(_col(row, "hidden"))
            online = str(_col(row, "status") or "").strip().upper() == "Y"
            status = Product.Status.INACTIVE if (hidden or not online) else Product.Status.ACTIVE

            # Quantity / unlimited
            stock, unlimited = _parse_qty(_col(row, "quantity"))
            # Also check the explicit unlimited_qty flag
            if _parse_bool(_col(row, "unlimited_qty")):
                unlimited = True

            # Prices
            current_base_price = float(_col(row, "base_price") or 0)
            sale_price = _parse_price(_col(row, "sale_price"))

            # Tags (newline-separated)
            tags_raw = _col(row, "tags")
            tags = [t.strip() for t in str(tags_raw).split("\n") if t.strip()] if tags_raw else []

            # Categories: build full parent-child hierarchy from Shopline multi-line format
            category = None
            cats_raw = _col(row, "categories")
            if cats_raw:
                category = _build_category_hierarchy(str(cats_raw))

            # Date fields
            pub = _col(row, "publish_at")
            avail_s = _col(row, "avail_start")
            avail_e = _col(row, "avail_end")

            current_data = {
                "name": name,
                "name_zh": _parse_str(name_zh),
                "summary": _parse_str(_col(row, "summary_en")),
                "summary_zh": _parse_str(_col(row, "summary_zh")),
                "base_price": current_base_price,
                "sale_price": sale_price,
                "cost": _parse_price(_col(row, "cost")),
                "sku": _parse_str(_col(row, "sku")),
                "stock": stock,
                "unlimited_stock": unlimited,
                "weight": _parse_price(_col(row, "weight")),
                "brand": _parse_str(_col(row, "brand")),
                "tags": tags,
                "promo_label": _parse_str(_col(row, "promo_label_en")),
                "promo_label_zh": _parse_str(_col(row, "promo_label_zh")),
                "hide_price": _parse_bool(_col(row, "hide_price")),
                "is_preorder": _parse_bool(_col(row, "preorder")),
                "preorder_note": _parse_str(_col(row, "preorder_note_en")),
                "preorder_note_zh": _parse_str(_col(row, "preorder_note_zh")),
                "exclude_from_discount": _parse_bool(_col(row, "exclude_discount")),
                "seo_title": _parse_str(_col(row, "seo_title_en")),
                "seo_title_zh": _parse_str(_col(row, "seo_title_zh")),
                "seo_description": _parse_str(_col(row, "seo_desc_en")),
                "seo_description_zh": _parse_str(_col(row, "seo_desc_zh")),
                "seo_keywords": _parse_str(_col(row, "seo_keywords")),
                "publish_at": pub if isinstance(pub, datetime) else None,
                "available_start": avail_s if isinstance(avail_s, datetime) else None,
                "available_end": avail_e if isinstance(avail_e, datetime) else None,
                "status": status,
                "category": category,
                "images": [],
            }

        # ── Variant row ──────────────────────────────────────────────────
        var_name_zh = _col(row, "var_name_zh")
        var_name_en = _col(row, "var_name_en")
        var_raw_price = _col(row, "var_price")

        if var_name_zh or var_name_en or var_raw_price:
            var_stock, var_unlimited = _parse_qty(_col(row, "var_qty"))
            var_price = _parse_price(var_raw_price, fallback=current_base_price)
            if var_price is None:
                var_price = current_base_price  # 價格一致 fallback

            var_sale = _parse_price(_col(row, "var_sale_price"))

            current_variants.append({
                "name": _parse_str(var_name_zh) or _parse_str(var_name_en) or "預設",
                "name_zh": _parse_str(var_name_zh),
                "sku": _parse_str(_col(row, "var_sku")),
                "price": var_price,
                "sale_price": var_sale,
                "cost": _parse_price(_col(row, "var_cost")),
                "stock": var_stock,
                "weight": _parse_price(_col(row, "var_weight")),
                "barcode": _parse_str(_col(row, "barcode")),
                "mpn": _parse_str(_col(row, "mpn")),
            })

    # Flush last product
    try:
        flush_product()
    except Exception as e:
        errors.append(f"最後一筆: {e}")
        logger.error("bulk_import flush error (last row): %s", e, exc_info=True)

    summary = f"匯入完成：新增 {created} 筆，更新 {updated} 筆。"
    if errors:
        summary += f" 錯誤 {len(errors)} 筆。"
        for err in errors[:5]:
            messages.warning(request, err)
    logger.info("bulk_import by %s: created=%d updated=%d errors=%d",
                request.user, created, updated, len(errors))
    messages.success(request, summary)
    context = {
        **admin.site.each_context(request),
        "title": "批量匯入商品",
        "result": {"created": created, "updated": updated, "errors": errors},
    }
    return render(request, "admin/products/bulk_import.html", context)
