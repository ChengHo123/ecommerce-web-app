from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.products.models import Product, ProductVariant
from .models import Cart, CartItem


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related("product", "variant").all()
    return render(request, "cart/cart.html", {"cart": cart, "items": items})


@login_required
def cart_data(request):
    """JSON endpoint for the mini cart drawer."""
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related("product", "variant").all()
    return JsonResponse({
        'count': cart.item_count,
        'total': str(cart.total),
        'items': [
            {
                'id': item.id,
                'product_name': item.product.name_zh or item.product.name,
                'product_slug': item.product.slug,
                'product_image': item.product.first_image or '',
                'variant_name': (item.variant.name_zh or item.variant.name) if item.variant else '',
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal),
            }
            for item in items
        ],
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status=Product.Status.ACTIVE)
    variant_id = request.POST.get("variant_id") or request.POST.get("variant")
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)

    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity"])

    if _is_ajax(request):
        return JsonResponse({
            'ok': True,
            'cart_count': cart.item_count,
            'product_name': product.name_zh or product.name,
        })

    messages.success(request, f"{product.name_zh or product.name} 已加入購物車。")
    next_url = request.POST.get("next", "/cart/")
    return redirect(next_url)


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        item.delete()
        item_subtotal = '0'
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        item_subtotal = str(item.subtotal)

    if _is_ajax(request):
        cart = _get_or_create_cart(request.user)
        return JsonResponse({
            'ok': True,
            'cart_count': cart.item_count,
            'cart_total': str(cart.total),
            'item_subtotal': item_subtotal,
        })

    return redirect("/cart/")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()

    if _is_ajax(request):
        cart = _get_or_create_cart(request.user)
        return JsonResponse({
            'ok': True,
            'cart_count': cart.item_count,
            'cart_total': str(cart.total),
        })

    return redirect("/cart/")
