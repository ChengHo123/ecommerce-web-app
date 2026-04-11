import logging
import uuid
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from apps.cart.models import Cart, CartItem
from apps.coupons.models import Coupon, CouponUsage
from apps.products.models import Product, ProductVariant
from .models import Order, OrderItem

logger = logging.getLogger("apps.orders")


def _generate_order_no() -> str:
    return f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


@login_required
def checkout(request):
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        messages.warning(request, "購物車是空的。")
        return redirect("/cart/")

    items = cart.items.select_related("product", "variant").all()
    if not items.exists():
        messages.warning(request, "購物車是空的。")
        return redirect("/cart/")

    return render(request, "checkout/checkout.html", {"cart": cart, "items": items})


@login_required
def place_order(request):
    if request.method != "POST":
        return redirect("/checkout/")

    try:
        cart = request.user.cart
        cart_items = list(cart.items.select_related("product", "variant").all())
    except (Cart.DoesNotExist, AttributeError):
        messages.error(request, "購物車是空的。")
        return redirect("/cart/")

    if not cart_items:
        messages.error(request, "購物車是空的。")
        return redirect("/cart/")

    logistics_type = request.POST.get("logistics_type", "home")
    payment_method = request.POST.get("payment_method", "linepay")
    buyer_note = request.POST.get("buyer_note", "")
    coupon_code = request.POST.get("coupon_code", "").strip().upper()

    # Build shipping address
    shipping_address = None
    cvs_store_id = cvs_store_name = cvs_type = None

    if logistics_type == "home":
        shipping_address = {
            "recipient": request.POST.get("recipient", ""),
            "phone": request.POST.get("phone", ""),
            "zip_code": request.POST.get("zip_code", ""),
            "city": request.POST.get("city", ""),
            "district": request.POST.get("district", ""),
            "address": request.POST.get("address", ""),
        }
    else:
        cvs_store_id = request.POST.get("cvs_store_id", "")
        cvs_store_name = request.POST.get("cvs_store_name", "")
        cvs_type = request.POST.get("cvs_type", "")

    # Calculate total
    total = 0.0
    order_items_data = []
    for item in cart_items:
        price = float(item.unit_price)
        total += price * item.quantity
        order_items_data.append({
            "product": item.product,
            "variant": item.variant,
            "quantity": item.quantity,
            "unit_price": price,
            "product_name": item.product.name_zh or item.product.name,
            "variant_name": item.variant.name_zh or item.variant.name if item.variant else None,
        })

    # Apply coupon
    discount_amount = 0.0
    coupon = None
    if coupon_code:
        from django.utils import timezone
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if (not coupon.expires_at or coupon.expires_at >= timezone.now()) and \
               (not coupon.usage_limit or coupon.used_count < coupon.usage_limit) and \
               total >= float(coupon.min_amount):
                discount_amount = coupon.calculate_discount(total)
        except Coupon.DoesNotExist:
            pass

    final_total = total - discount_amount

    # Create order
    order = Order.objects.create(
        order_no=_generate_order_no(),
        user=request.user,
        total=final_total,
        discount_amount=discount_amount,
        payment_method=payment_method,
        logistics_type=logistics_type,
        shipping_address=shipping_address,
        cvs_store_id=cvs_store_id,
        cvs_store_name=cvs_store_name,
        cvs_type=cvs_type,
        buyer_note=buyer_note,
        coupon=coupon,
    )

    for item_data in order_items_data:
        OrderItem.objects.create(order=order, **item_data)

    if coupon:
        coupon.used_count += 1
        coupon.save(update_fields=["used_count"])
        CouponUsage.objects.create(coupon=coupon, user=request.user, order=order)

    # Clear cart
    cart.items.all().delete()

    logger.info("order created: %s user=%s total=%s method=%s logistics=%s",
                order.order_no, request.user, final_total, payment_method, logistics_type)

    request.session["last_order_id"] = order.id
    return redirect(f"/checkout/payment/{order.id}/")


@login_required
def payment_redirect(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.payment_method == "linepay":
        from services.line_pay import create_line_pay_payment
        try:
            payment_url = create_line_pay_payment(order, request)
        except Exception:
            logger.exception("LINE Pay request failed for order %s", order.order_no)
            payment_url = None
        if payment_url:
            logger.info("LINE Pay redirect: order=%s", order.order_no)
            return redirect(payment_url)
    elif order.payment_method == "stripe":
        from services.stripe_service import create_stripe_session
        try:
            checkout_url = create_stripe_session(order, request)
        except Exception:
            logger.exception("Stripe session failed for order %s", order.order_no)
            checkout_url = None
        if checkout_url:
            logger.info("Stripe redirect: order=%s", order.order_no)
            return redirect(checkout_url)

    logger.error("payment redirect failed: order=%s method=%s", order.order_no, order.payment_method)
    messages.error(request, "無法建立付款請求，請重試。")
    return redirect(f"/orders/{order.id}/")


# ── ECPay CVS Map ──────────────────────────────────────────────────────────

@login_required
@require_GET
def cvs_map_page(request):
    """
    Opens in a popup. Renders a self-submitting form to ECPay's CVS map.
    Query params: cvs_type = UNIMART | FAMI | HILIFE | OKMART
    """
    from services.ecpay_logistics import build_map_form
    cvs_type = request.GET.get("cvs_type", "UNIMART").upper()
    callback_url = request.build_absolute_uri("/checkout/cvs-callback/")
    form_data = build_map_form(cvs_type, server_reply_url=callback_url)
    return render(request, "checkout/cvs_map.html", {"form": form_data})


@csrf_exempt
@require_POST
def cvs_callback(request):
    """
    ECPay POSTs store data here after user selects a store.
    Saves to session and renders a close-popup page.
    Note: ECPay calls this from their servers — no Django session cookie,
    so we use the MerchantTradeNo to match the waiting session.
    We store in a server-side cache keyed by trade number instead.
    """
    from django.core.cache import cache
    from services.ecpay_logistics import verify_callback

    data = request.POST.dict()

    # Verify signature (skip in sandbox if signature is empty)
    if data.get("CheckMacValue") and not verify_callback(data):
        return render(request, "checkout/cvs_callback_done.html", {"error": "驗證失敗"})

    store = {
        "cvs_type":      data.get("LogisticsSubType", ""),
        "cvs_store_id":  data.get("CVSStoreID", ""),
        "cvs_store_name": data.get("CVSStoreName", ""),
        "cvs_address":   data.get("CVSAddress", ""),
        "cvs_telephone": data.get("CVSTelephone", ""),
    }

    # Cache by trade_no for 10 minutes so the checkout page can pick it up
    trade_no = data.get("MerchantTradeNo", "")
    if trade_no:
        cache.set(f"cvs_store_{trade_no}", store, timeout=600)

    return render(request, "checkout/cvs_callback_done.html", {
        "store": store,
        "trade_no": trade_no,
    })


@login_required
@require_GET
def cvs_store_api(request):
    """
    Ajax endpoint: returns selected store from cache by trade_no.
    Called by the checkout page polling after the popup opens.
    """
    from django.core.cache import cache
    trade_no = request.GET.get("trade_no", "")
    if not trade_no:
        return JsonResponse({"store": None})
    store = cache.get(f"cvs_store_{trade_no}")
    return JsonResponse({"store": store})
