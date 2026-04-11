from pathlib import Path
from django.urls import reverse_lazy
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost 127.0.0.1").split()

UNFOLD = {
    "SITE_TITLE": "TwoRabbits 後台",
    "SITE_HEADER": "TwoRabbits",
    "SITE_URL": "/",
    "SITE_SYMBOL": "storefront",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "6px",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "separator": False,
                "items": [
                    {
                        "title": "儀表板",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_staff,
                    },
                ],
            },
            {
                "title": "商品管理",
                "separator": True,
                "items": [
                    {
                        "title": "所有商品",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },
                    {
                        "title": "商品分類",
                        "icon": "category",
                        "link": reverse_lazy("admin:products_category_changelist"),
                    },
                    {
                        "title": "批量匯入",
                        "icon": "upload_file",
                        "link": reverse_lazy("bulk_import"),
                    },
                ],
            },
            {
                "title": "訂單管理",
                "separator": True,
                "items": [
                    {
                        "title": "所有訂單",
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                ],
            },
            {
                "title": "會員管理",
                "separator": True,
                "items": [
                    {
                        "title": "所有會員",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                ],
            },
            {
                "title": "行銷工具",
                "separator": True,
                "items": [
                    {
                        "title": "優惠券",
                        "icon": "sell",
                        "link": reverse_lazy("admin:coupons_coupon_changelist"),
                    },
                ],
            },
        ],
    },
}

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "apps.accounts",
    "apps.products",
    "apps.orders",
    "apps.cart",
    "apps.coupons",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.cart.context_processors.cart_count",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "ecommerce"),
        "USER": os.environ.get("DB_USER", "ecommerce"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "ecommerce_pass"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hant"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ── Media / Object Storage ─────────────────────────────────────────────────
# 切換存儲後端只需修改這裡，程式碼不需要改動。
#
# 目前：本機 filesystem（開發用）
# 換成 Cloudflare R2 / AWS S3：
#   pip install django-storages boto3
#   "default": {
#       "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
#       "OPTIONS": {
#           "bucket_name":        os.environ.get("S3_BUCKET_NAME"),
#           "access_key":         os.environ.get("S3_ACCESS_KEY"),
#           "secret_key":         os.environ.get("S3_SECRET_KEY"),
#           "endpoint_url":       os.environ.get("S3_ENDPOINT_URL"),   # R2 專用
#           "custom_domain":      os.environ.get("S3_CUSTOM_DOMAIN"),  # CDN 域名
#           "file_overwrite":     False,
#           "default_acl":        None,
#       }
#   }
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Logging ────────────────────────────────────────────────────────────────
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # One-liner for app.log / request.log
        "verbose": {
            "format": "[{asctime}] {levelname:<8} {name} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Compact for terminal
        "console": {
            "format": "{levelname:<8} {name}: {message}",
            "style": "{",
        },
        # Multi-line with full context + traceback — used by error.log
        "rich": {
            "()": "ecommerce.log_handlers.RichFormatter",
        },
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true":  {"()": "django.utils.log.RequireDebugTrue"},
        "ignore_noise_404":    {"()": "ecommerce.log_handlers.IgnoreNoise404"},
        # ↑ drops /.well-known/ and other browser auto-probe 404s from error.log
    },
    # Use a factory callable so we can set .suffix after construction.
    # Rotated files are renamed to  <base>.log.YYYY-MM-DD automatically.
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "filters": ["require_debug_true"],
        },
        "app_file": {
            "()": "ecommerce.log_handlers.make_timed_handler",
            "filename": str(_LOG_DIR / "app.log"),
            "backup_count": 30,
            "formatter": "verbose",
        },
        "error_file": {
            "()": "ecommerce.log_handlers.make_timed_handler",
            "filename": str(_LOG_DIR / "error.log"),
            "backup_count": 60,
            "level": "WARNING",
            "formatter": "rich",
            "filters": ["ignore_noise_404"],
        },
        "request_file": {
            "()": "ecommerce.log_handlers.make_timed_handler",
            "filename": str(_LOG_DIR / "request.log"),
            "backup_count": 14,
            "formatter": "verbose",
        },
        "security_file": {
            "()": "ecommerce.log_handlers.make_timed_handler",
            "filename": str(_LOG_DIR / "security.log"),
            "backup_count": 90,
            "level": "WARNING",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "request_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "security_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "services": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "app_file", "error_file"],
        "level": "WARNING",
    },
}

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# LINE Login
LINE_LOGIN_CHANNEL_ID = os.environ.get("LINE_LOGIN_CHANNEL_ID", "")
LINE_LOGIN_CHANNEL_SECRET = os.environ.get("LINE_LOGIN_CHANNEL_SECRET", "")
LINE_LOGIN_REDIRECT_URI = os.environ.get("LINE_LOGIN_REDIRECT_URI", "http://localhost:8000/auth/line/callback/")

# LINE Pay
LINE_PAY_CHANNEL_ID = os.environ.get("LINE_PAY_CHANNEL_ID", "")
LINE_PAY_CHANNEL_SECRET = os.environ.get("LINE_PAY_CHANNEL_SECRET", "")
LINE_PAY_IS_SANDBOX = os.environ.get("LINE_PAY_IS_SANDBOX", "True") == "True"
LINE_PAY_CONFIRM_URL = os.environ.get("LINE_PAY_CONFIRM_URL", "http://localhost:8000/checkout/confirm/")
LINE_PAY_CANCEL_URL = os.environ.get("LINE_PAY_CANCEL_URL", "http://localhost:8000/checkout/cancel/")

# Stripe
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

# ECPay
ECPAY_MERCHANT_ID = os.environ.get("ECPAY_MERCHANT_ID", "2000132")
ECPAY_HASH_KEY = os.environ.get("ECPAY_HASH_KEY", "5294y06JbISpM5x9")
ECPAY_HASH_IV = os.environ.get("ECPAY_HASH_IV", "v77hoKGq4kWxNNIS")
ECPAY_IS_SANDBOX = os.environ.get("ECPAY_IS_SANDBOX", "True") == "True"
