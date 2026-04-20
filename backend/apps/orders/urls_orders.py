from django.urls import path
from .views_orders import order_list, order_detail, order_confirm
from .views_logistics import logistics_callback

urlpatterns = [
    path("", order_list, name="order_list"),
    path("confirm/", order_confirm, name="order_confirm"),
    path("logistics-callback/", logistics_callback, name="logistics_callback"),
    path("<int:order_id>/", order_detail, name="order_detail"),
]
