from django.urls import path
from .views_orders import order_list, order_detail, order_confirm

urlpatterns = [
    path("", order_list, name="order_list"),
    path("confirm/", order_confirm, name="order_confirm"),
    path("<int:order_id>/", order_detail, name="order_detail"),
]
