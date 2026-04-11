from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Order


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(orders, 10)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "orders/list.html", {"page": page})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"),
        pk=order_id,
        user=request.user,
    )
    return render(request, "orders/detail.html", {"order": order})


@login_required
def order_confirm(request):
    order_id = request.session.get("last_order_id")
    if not order_id:
        return redirect("/orders/")
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "checkout/confirm.html", {"order": order})
