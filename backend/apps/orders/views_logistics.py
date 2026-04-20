import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from services.ecpay_logistics import verify_callback
from .models import Order

logger = logging.getLogger("apps.orders")

# ECPay RtnCode → our logistics status mapping
_STATUS_MAP = {
    "300":  Order.LogisticsStatus.CREATED,    # 訂單處理中
    "2030": Order.LogisticsStatus.IN_TRANSIT,  # 配達中
    "2063": Order.LogisticsStatus.ARRIVED,     # 已送達門市
    "2067": Order.LogisticsStatus.ARRIVED,     # 已送達門市 (pickup ready)
    "2073": Order.LogisticsStatus.DELIVERED,   # 已取貨
    "3024": Order.LogisticsStatus.DELIVERED,   # 宅配簽收
}


@csrf_exempt
@require_POST
def logistics_callback(request):
    """
    ECPay logistics status update callback.
    ECPay POSTs status changes here as shipment progresses.
    Must reply with "1|OK" to acknowledge.
    """
    data = request.POST.dict()

    # Verify CheckMacValue signature
    if not verify_callback(data):
        logger.warning("logistics callback signature mismatch: %s", data)
        return HttpResponse("0|CheckMacValue Error")

    trade_no = data.get("MerchantTradeNo", "")
    rtn_code = data.get("RtnCode", "")
    rtn_msg = data.get("RtnMsg", "")
    all_pay_logistics_id = data.get("AllPayLogisticsID", "")

    logger.info(
        "logistics callback: trade_no=%s rtn_code=%s msg=%s ecpay_id=%s",
        trade_no, rtn_code, rtn_msg, all_pay_logistics_id,
    )

    # Find matching order by tracking_no (which stores the MerchantTradeNo)
    order = Order.objects.filter(tracking_no=trade_no).first()
    if not order:
        logger.warning("logistics callback: no matching order for trade_no=%s", trade_no)
        return HttpResponse("1|OK")

    new_status = _STATUS_MAP.get(rtn_code)
    if new_status:
        old_status = order.logistics_status
        order.logistics_status = new_status
        # Auto-advance order status
        if new_status == Order.LogisticsStatus.IN_TRANSIT:
            order.status = Order.Status.SHIPPED
        elif new_status in (Order.LogisticsStatus.ARRIVED, Order.LogisticsStatus.DELIVERED):
            order.status = Order.Status.DELIVERED
        order.save(update_fields=["logistics_status", "status"])
        logger.info("order %s logistics updated: %s → %s", order.order_no, rtn_code, new_status)

        # Send shipping notification email on first transit event
        if new_status == Order.LogisticsStatus.IN_TRANSIT and old_status != Order.LogisticsStatus.IN_TRANSIT:
            from services.email_notify import send_order_shipped
            send_order_shipped(order)

    return HttpResponse("1|OK")
