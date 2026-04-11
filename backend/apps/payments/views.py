import json
import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.orders.models import Order
from .models import Payment


@login_required
def line_pay_confirm(request):
    transaction_id = request.GET.get("transactionId")
    order_id = request.GET.get("orderId")

    order = get_object_or_404(Order, pk=order_id, user=request.user)

    from services.line_pay import confirm_line_pay_payment
    success = confirm_line_pay_payment(order, transaction_id)

    if success:
        order.payment_status = Order.PaymentStatus.PAID
        order.status = Order.Status.PAID
        order.save(update_fields=["payment_status", "status"])
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "provider": Payment.Provider.LINEPAY,
                "transaction_id": transaction_id,
                "amount": order.total,
                "status": Payment.Status.COMPLETED,
            },
        )
        request.session["last_order_id"] = order.id
        return redirect("/orders/confirm/")

    return redirect(f"/orders/{order.id}/")


@login_required
def line_pay_cancel(request):
    order_id = request.GET.get("orderId")
    if order_id:
        Order.objects.filter(pk=order_id, user=request.user).update(
            status=Order.Status.CANCELLED
        )
    return redirect("/orders/")


@login_required
def stripe_success(request):
    session_id = request.GET.get("session_id")
    order_id = request.session.get("stripe_order_id")
    if order_id:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        order.payment_status = Order.PaymentStatus.PAID
        order.status = Order.Status.PAID
        order.save(update_fields=["payment_status", "status"])
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "provider": Payment.Provider.STRIPE,
                "transaction_id": session_id,
                "amount": order.total,
                "status": Payment.Status.COMPLETED,
            },
        )
        request.session["last_order_id"] = order.id
    return redirect("/orders/confirm/")


@login_required
def stripe_cancel(request):
    return redirect("/cart/")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_no = session.get("metadata", {}).get("order_no")
        if order_no:
            Order.objects.filter(order_no=order_no).update(
                payment_status=Order.PaymentStatus.PAID,
                status=Order.Status.PAID,
            )

    return HttpResponse(status=200)
