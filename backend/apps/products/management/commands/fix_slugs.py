"""
Fix non-ASCII (e.g. Chinese) product slugs.
Usage: python manage.py fix_slugs
"""
import re
from django.core.management.base import BaseCommand
from apps.products.models import Product


def _ascii_slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\x00-\x7f]", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def _unique_slug(base: str, exclude_pk: int) -> str:
    slug = base or f"product-{exclude_pk}"
    counter = 1
    while Product.objects.filter(slug=slug).exclude(pk=exclude_pk).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _has_non_ascii(s: str) -> bool:
    return bool(re.search(r"[^\x00-\x7f]", s))


class Command(BaseCommand):
    help = "Re-generate ASCII slugs for products that have non-ASCII (Chinese) slugs"

    def handle(self, *args, **options):
        qs = Product.objects.all()
        fixed = 0
        for product in qs:
            if not _has_non_ascii(product.slug):
                continue
            base = (
                _ascii_slugify(product.name or "")
                or _ascii_slugify(product.sku or "")
                or f"product-{product.pk}"
            )
            new_slug = _unique_slug(base, exclude_pk=product.pk)
            self.stdout.write(f"  {product.slug!r} → {new_slug!r}")
            product.slug = new_slug
            product.save(update_fields=["slug"])
            fixed += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone. Fixed {fixed} slug(s)."))
