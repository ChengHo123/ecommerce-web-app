from django.urls import path
from .views import validate_coupon

urlpatterns = [
    path("validate/", validate_coupon, name="validate_coupon"),
]
