from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<str:slug>/", views.product_detail, name="product_detail"),
    path("admin-tools/bulk-import/", views.bulk_import, name="bulk_import"),
]
