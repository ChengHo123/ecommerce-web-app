from django.urls import path
from . import views

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("place/", views.place_order, name="place_order"),
    path("payment/<int:order_id>/", views.payment_redirect, name="payment_redirect"),
    # ECPay CVS map
    path("cvs-map/", views.cvs_map_page, name="cvs_map_page"),
    path("cvs-callback/", views.cvs_callback, name="cvs_callback"),
    path("cvs-store/", views.cvs_store_api, name="cvs_store_api"),
]
