from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Coupon


@login_required
@require_POST
def validate_coupon(request):
    code = request.POST.get("code", "").strip().upper()
    total = float(request.POST.get("total", 0))

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "message": "優惠券不存在或已失效"})

    if coupon.expires_at and coupon.expires_at < timezone.now():
        return JsonResponse({"valid": False, "message": "優惠券已過期"})

    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return JsonResponse({"valid": False, "message": "優惠券已達使用上限"})

    if total < float(coupon.min_amount):
        return JsonResponse({"valid": False, "message": f"訂單金額需達 ${coupon.min_amount} 才可使用"})

    discount = coupon.calculate_discount(total)
    return JsonResponse({
        "valid": True,
        "discount": round(discount, 2),
        "message": f"優惠券有效，折抵 ${discount:.0f}",
    })
