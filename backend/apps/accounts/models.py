from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        user = self.model(name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name="Admin", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = "user", "一般用戶"
        ADMIN = "admin", "管理員"

    line_user_id = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    avatar = models.URLField(max_length=500, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
        verbose_name = "用戶"
        verbose_name_plural = "用戶"

    def __str__(self):
        return f"{self.name} ({self.email or self.line_user_id or self.pk})"
