"""
Email notification service for order events.

Uses Django's built-in email backend. Configure EMAIL_BACKEND in settings.py
for production (e.g., SMTP, SES, SendGrid).
"""
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger("services")


def send_order_confirmed(order):
    """Send order confirmation email to the customer."""
    user = order.user
    if not user.email:
        logger.info("skip order_confirmed email: user=%s has no email", user.pk)
        return

    items = order.items.all()
    context = {
        "order": order,
        "items": items,
        "user_name": user.name,
    }

    html_body = render_to_string("emails/order_confirmed.html", context)
    text_body = (
        f"訂單確認 — {order.order_no}\n\n"
        f"{user.name}，您好！感謝您的訂購。\n"
        f"訂單金額：${order.total}\n"
        f"付款方式：{order.get_payment_method_display()}\n"
    )

    msg = EmailMultiAlternatives(
        subject=f"[兔窩] 訂單確認 — {order.order_no}",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send(fail_silently=False)
        logger.info("order_confirmed email sent: order=%s to=%s", order.order_no, user.email)
    except Exception:
        logger.exception("order_confirmed email failed: order=%s to=%s", order.order_no, user.email)


def send_order_shipped(order):
    """Send shipping notification email to the customer."""
    user = order.user
    if not user.email:
        logger.info("skip order_shipped email: user=%s has no email", user.pk)
        return

    items = order.items.all()
    context = {
        "order": order,
        "items": items,
        "user_name": user.name,
    }

    html_body = render_to_string("emails/order_shipped.html", context)
    text_body = (
        f"出貨通知 — {order.order_no}\n\n"
        f"{user.name}，您好！您的訂單已出貨。\n"
    )
    if order.tracking_no:
        text_body += f"物流單號：{order.tracking_no}\n"

    msg = EmailMultiAlternatives(
        subject=f"[兔窩] 出貨通知 — {order.order_no}",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send(fail_silently=False)
        logger.info("order_shipped email sent: order=%s to=%s", order.order_no, user.email)
    except Exception:
        logger.exception("order_shipped email failed: order=%s to=%s", order.order_no, user.email)
