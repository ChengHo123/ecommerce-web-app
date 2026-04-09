import hmac
import hashlib
import base64
import uuid
import json
from datetime import datetime, timezone
import httpx
from app.core.config import settings


def _generate_signature(channel_secret: str, uri: str, request_body: str, nonce: str) -> str:
    """Generate LINE Pay HMAC-SHA256 signature"""
    message = channel_secret + uri + request_body + nonce
    signature = hmac.new(channel_secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def _get_headers(uri: str, body: dict) -> dict:
    nonce = uuid.uuid4().hex
    body_str = json.dumps(body)
    signature = _generate_signature(settings.LINE_PAY_CHANNEL_SECRET, uri, body_str, nonce)
    return {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": settings.LINE_PAY_CHANNEL_ID,
        "X-LINE-Authorization-Nonce": nonce,
        "X-LINE-Authorization": signature,
    }


async def request_line_pay(order) -> dict:
    """Create LINE Pay payment request"""
    uri = "/v3/payments/request"
    body = {
        "amount": int(order.total),
        "currency": "TWD",
        "orderId": order.order_no,
        "packages": [
            {
                "id": f"pkg_{order.order_no}",
                "amount": int(order.total),
                "products": [
                    {
                        "name": f"訂單 {order.order_no}",
                        "quantity": 1,
                        "price": int(order.total),
                    }
                ],
            }
        ],
        "redirectUrls": {
            "confirmUrl": settings.LINE_PAY_CONFIRM_URL,
            "cancelUrl": settings.LINE_PAY_CANCEL_URL,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.line_pay_base_url}{uri}",
            headers=_get_headers(uri, body),
            json=body,
        )
        return response.json()


async def confirm_line_pay(transaction_id: str, amount: float) -> dict:
    """Confirm LINE Pay payment"""
    uri = f"/v3/payments/{transaction_id}/confirm"
    body = {"amount": int(amount), "currency": "TWD"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.line_pay_base_url}{uri}",
            headers=_get_headers(uri, body),
            json=body,
        )
        return response.json()
