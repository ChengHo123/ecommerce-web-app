import hashlib
import urllib.parse
from datetime import datetime
import httpx
from app.core.config import settings


def _ecpay_checksum(params: dict) -> str:
    """Generate ECPay CheckMacValue"""
    sorted_params = sorted(params.items())
    query = "&".join(f"{k}={v}" for k, v in sorted_params)
    raw = f"HashKey={settings.ECPAY_HASH_KEY}&{query}&HashIV={settings.ECPAY_HASH_IV}"
    encoded = urllib.parse.quote_plus(raw).lower()
    return hashlib.sha256(encoded.encode()).hexdigest().upper()


def get_ecpay_cvs_map_url(cvs_type: str = "UNIMART") -> str:
    """Get ECPay CVS store map selection URL"""
    base = "https://logistics-stage.ecpay.com.tw" if settings.ECPAY_IS_SANDBOX else "https://logistics.ecpay.com.tw"
    params = {
        "MerchantID": settings.ECPAY_MERCHANT_ID,
        "LogisticsType": "CVS",
        "LogisticsSubType": cvs_type,
        "IsCollection": "N",
        "ServerReplyURL": f"http://localhost:8000/logistics/cvs-callback",  # update in prod
    }
    check = _ecpay_checksum(params)
    params["CheckMacValue"] = check
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base}/Express/map?{query}"


async def create_cvs_shipment(order) -> str:
    """Create ECPay CVS (convenience store) shipment"""
    now = datetime.now()
    params = {
        "MerchantID": settings.ECPAY_MERCHANT_ID,
        "MerchantTradeNo": order.order_no,
        "MerchantTradeDate": now.strftime("%Y/%m/%d %H:%M:%S"),
        "LogisticsType": "CVS",
        "LogisticsSubType": order.cvs_type or "UNIMART",
        "GoodsAmount": str(int(order.total)),
        "IsCollection": "N",
        "GoodsName": f"訂單{order.order_no}",
        "SenderName": "商店名稱",
        "SenderPhone": "0912345678",
        "ReceiverName": order.shipping_address.get("recipient_name", "") if order.shipping_address else "",
        "ReceiverPhone": order.shipping_address.get("phone", "") if order.shipping_address else "",
        "ReceiverStoreID": order.cvs_store_id or "",
        "ServerReplyURL": f"http://localhost:8000/logistics/ecpay-callback",
    }
    params["CheckMacValue"] = _ecpay_checksum(params)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ecpay_logistics_url}/Create",
            data=params,
        )
        result = dict(urllib.parse.parse_qsl(response.text))
        return result.get("AllPayLogisticsID", "")


async def create_home_shipment(order) -> str:
    """Create ECPay home delivery (黑貓/新竹) shipment"""
    now = datetime.now()
    addr = order.shipping_address or {}
    params = {
        "MerchantID": settings.ECPAY_MERCHANT_ID,
        "MerchantTradeNo": order.order_no,
        "MerchantTradeDate": now.strftime("%Y/%m/%d %H:%M:%S"),
        "LogisticsType": "Home",
        "LogisticsSubType": "TCAT",  # 黑貓宅急便
        "GoodsAmount": str(int(order.total)),
        "GoodsWeight": "1",
        "GoodsName": f"訂單{order.order_no}",
        "SenderName": "商店名稱",
        "SenderPhone": "0912345678",
        "SenderZipCode": "100",
        "SenderAddress": "台北市中正區重慶南路一段122號",
        "ReceiverName": addr.get("recipient_name", ""),
        "ReceiverPhone": addr.get("phone", ""),
        "ReceiverZipCode": addr.get("postal_code", ""),
        "ReceiverAddress": f"{addr.get('city', '')}{addr.get('district', '')}{addr.get('address', '')}",
        "ServerReplyURL": f"http://localhost:8000/logistics/ecpay-callback",
    }
    params["CheckMacValue"] = _ecpay_checksum(params)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ecpay_logistics_url}/Create",
            data=params,
        )
        result = dict(urllib.parse.parse_qsl(response.text))
        return result.get("AllPayLogisticsID", "")
