from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import display
from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ("name", "email", "line_user_id", "role_badge", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("name", "email", "line_user_id", "phone")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("個人資訊", {
            "fields": ("name", "phone", "avatar", "line_user_id"),
            "classes": ["tab"],
        }),
        ("權限", {
            "fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ["tab"],
        }),
        ("時間", {
            "fields": ("created_at", "updated_at", "last_login"),
            "classes": ["tab"],
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "role", "is_staff"),
        }),
    )
    filter_horizontal = ("groups", "user_permissions")

    @display(description="角色", label={
        "admin": "success",
        "user": "info",
    })
    def role_badge(self, obj):
        return obj.role
