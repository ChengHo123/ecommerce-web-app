import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def safe_json(value):
    """Serialize value to JSON string safe for inline <script> use."""
    return mark_safe(json.dumps(value, ensure_ascii=False))
