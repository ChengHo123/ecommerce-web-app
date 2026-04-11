from django.urls import path
from . import views

urlpatterns = [
    path("line/confirm/", views.line_pay_confirm, name="line_pay_confirm"),
    path("line/cancel/", views.line_pay_cancel, name="line_pay_cancel"),
    path("stripe/success/", views.stripe_success, name="stripe_success"),
    path("stripe/cancel/", views.stripe_cancel, name="stripe_cancel"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
