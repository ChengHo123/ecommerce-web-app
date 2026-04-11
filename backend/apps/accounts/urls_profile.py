from django.urls import path
from .views_profile import profile_view

urlpatterns = [
    path("", profile_view, name="profile"),
]
