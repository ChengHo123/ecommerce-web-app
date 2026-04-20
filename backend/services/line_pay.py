import hmac
import hashlib
import base64
import uuid
import json
import httpx
from django.conf import settings


def _sign(channel_secret: str, uri: str, body: str, nonce: str) -> str:
    message = channel_secret + uri + body + nonce
    signature = hmac.new(
        channel_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(signature).decode("utf-8")


def _base_url() -> str:
    if settings.LINE_PAY_IS_SANDBOX:
        return "https://sandbox-api-pay.line.me"
    return "https://api-pay.line.me"


def create_line_pay_payment(order, request) -> str | None:
    uri = "/v3/payments/request"
    nonce = uuid.uuid4().hex
    body_data = {
        "amount": int(order.total),
        "currency": "TWD",
        "orderId": str(order.id),
        "packages": [
            {
                "id": str(order.id),
                "amount": int(order.total),
                "name": "訂單付款",
                "products": [
                    {
                        "name": item.product_name,
                        "quantity": item.quantity,
                        "price": int(item.unit_price),
                    }
                    for item in order.items.all()
                ],
            }
        ],
        "redirectUrls": {
            "confirmUrl": settings.LINE_PAY_CONFIRM_URL + f"?orderId={order.id}",
            "cancelUrl": settings.LINE_PAY_CANCEL_URL + f"?orderId={order.id}",
        },
    }
    body_str = json.dumps(body_data)
    signature = _sign(settings.LINE_PAY_CHANNEL_SECRET, uri, body_str, nonce)

    try:
        resp = httpx.post(
            _base_url() + uri,
            content=body_str,
            headers={
                "Content-Type": "application/json",
                "X-LINE-ChannelId": settings.LINE_PAY_CHANNEL_ID,
                "X-LINE-Authorization-Nonce": nonce,
                "X-LINE-Authorization": signature,
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("returnCode") == "0000":
            return data["info"]["paymentUrl"]["web"]
    except Exception:
        pass
    return None


def refund_line_pay_payment(order) -> bool:
    """Refund a LINE Pay payment. Requires the Payment record with transaction_id."""
    from apps.payments.models import Payment
    try:
        payment = Payment.objects.get(order=order, provider=Payment.Provider.LINEPAY)
    except Payment.DoesNotExist:
        return False

    if not payment.transaction_id:
        return False

    uri = f"/v3/payments/{payment.transaction_id}/refund"
    nonce = uuid.uuid4().hex
    body_data = {}
    body_str = json.dumps(body_data)
    signature = _sign(settings.LINE_PAY_CHANNEL_SECRET, uri, body_str, nonce)

    try:
        resp = httpx.post(
            _base_url() + uri,
            content=body_str,
            headers={
                "Content-Type": "application/json",
                "X-LINE-ChannelId": settings.LINE_PAY_CHANNEL_ID,
                "X-LINE-Authorization-Nonce": nonce,
                "X-LINE-Authorization": signature,
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("returnCode") == "0000":
            payment.status = Payment.Status.REFUNDED
            payment.save(update_fields=["status"])
            return True
    except Exception:
        pass
    return False


def confirm_line_pay_payment(order, transaction_id: str) -> bool:
    uri = f"/v3/payments/{transaction_id}/confirm"
    nonce = uuid.uuid4().hex
    body_data = {"amount": int(order.total), "currency": "TWD"}
    body_str = json.dumps(body_data)
    signature = _sign(settings.LINE_PAY_CHANNEL_SECRET, uri, body_str, nonce)

    try:
        resp = httpx.post(
            _base_url() + uri,
            content=body_str,
            headers={
                "Content-Type": "application/json",
                "X-LINE-ChannelId": settings.LINE_PAY_CHANNEL_ID,
                "X-LINE-Authorization-Nonce": nonce,
                "X-LINE-Authorization": signature,
            },
            timeout=15,
        )
        data = resp.json()
        return data.get("returnCode") == "0000"
    except Exception:
        return False
