from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("apps.accounts.urls")),
    path("profile/", include("apps.accounts.urls_profile")),
    path("cart/", include("apps.cart.urls")),
    path("checkout/", include("apps.orders.urls")),
    path("orders/", include("apps.orders.urls_orders")),
    path("payment/", include("apps.payments.urls")),
    path("coupons/", include("apps.coupons.urls")),
    path("", include("apps.products.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
