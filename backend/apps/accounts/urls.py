from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("line/", views.line_login_redirect, name="line_login"),
    path("line/callback/", views.line_callback, name="line_callback"),
]
