"""
ECPay Logistics — CVS map store selection.

Flow:
  1. Frontend opens /checkout/cvs-map/?cvs_type=UNIMART  (new popup window)
  2. That page auto-POSTs a signed form to ECPay's map URL
  3. User picks a store; ECPay POSTs store data to ServerReplyURL
  4. ServerReplyURL (/checkout/cvs-callback/) saves data in Django session
     and renders a page that closes the popup
  5. Original window polls /checkout/cvs-store/ (JSON) until store appears
"""
import hashlib
import urllib.parse
import uuid
from datetime import datetime

from django.conf import settings


# ── ECPay endpoints ────────────────────────────────────────────────────────
def _map_url() -> str:
    if getattr(settings, "ECPAY_IS_SANDBOX", True):
        return "https://logistics-stage.ecpay.com.tw/Express/map"
    return "https://logistics.ecpay.com.tw/Express/map"


# ── CheckMacValue ──────────────────────────────────────────────────────────
def _check_mac(params: dict) -> str:
    """
    Compute ECPay CheckMacValue (SHA256).
    Sorted alphabetically, wrapped in HashKey/HashIV, URL-encoded, SHA256, upper.
    """
    key = settings.ECPAY_HASH_KEY
    iv  = settings.ECPAY_HASH_IV

    # Sort by key name (case-insensitive)
    sorted_items = sorted(params.items(), key=lambda x: x[0].lower())
    raw = "&".join(f"{k}={v}" for k, v in sorted_items)
    raw = f"HashKey={key}&{raw}&HashIV={iv}"

    # URL-encode following ECPay rules (same as payment API)
    encoded = urllib.parse.quote_plus(raw).lower()

    # Un-escape characters ECPay keeps literal
    for ch_from, ch_to in [
        ("%21", "!"), ("%28", "("), ("%29", ")"), ("%2a", "*"),
        ("%2d", "-"), ("%2e", "."), ("%5f", "_"),
    ]:
        encoded = encoded.replace(ch_from, ch_to)

    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_callback(post_data: dict) -> bool:
    """Return True if ECPay callback CheckMacValue is valid."""
    received = post_data.get("CheckMacValue", "")
    params = {k: v for k, v in post_data.items() if k != "CheckMacValue"}
    return _check_mac(params) == received.upper()


# ── Map form builder ───────────────────────────────────────────────────────
_CVS_SUBTYPE = {
    "UNIMART":  "UNIMART",   # 7-ELEVEN
    "FAMI":     "FAMI",      # 全家
    "HILIFE":   "HILIFE",    # 萊爾富
    "OKMART":   "OKMART",    # OK mart
}

_CVS_LABEL = {
    "UNIMART": "7-ELEVEN",
    "FAMI":    "全家",
    "HILIFE":  "萊爾富",
    "OKMART":  "OK mart",
}


def build_map_form(cvs_type: str, server_reply_url: str) -> dict:
    """
    Return a dict with:
      - action_url  : where to POST the form
      - fields      : list of (name, value) tuples to render as hidden inputs
    """
    subtype = _CVS_SUBTYPE.get(cvs_type.upper(), "UNIMART")

    # MerchantTradeNo must be ≤ 20 chars, unique
    trade_no = datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:4].upper()
    trade_no = trade_no[:20]

    params = {
        "MerchantID":       settings.ECPAY_MERCHANT_ID,
        "MerchantTradeNo":  trade_no,
        "LogisticsType":    "CVS",
        "LogisticsSubType": subtype,
        "IsCollection":     "N",
        "ServerReplyURL":   server_reply_url,
        "ExtraData":        "",
        "Device":           "0",
    }
    params["CheckMacValue"] = _check_mac(params)

    return {
        "action_url": _map_url(),
        "fields": list(params.items()),
        "cvs_label": _CVS_LABEL.get(cvs_type.upper(), cvs_type),
    }
