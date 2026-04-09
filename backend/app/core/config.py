from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ecommerce API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # LINE Login
    LINE_LOGIN_CHANNEL_ID: str = ""
    LINE_LOGIN_CHANNEL_SECRET: str = ""
    LINE_LOGIN_REDIRECT_URI: str = "http://localhost:5173/auth/line/callback"
    LINE_ADMIN_REDIRECT_URI: str = "http://localhost:5174/auth/line/callback"

    # LINE Pay
    LINE_PAY_CHANNEL_ID: str = ""
    LINE_PAY_CHANNEL_SECRET: str = ""
    LINE_PAY_IS_SANDBOX: bool = True
    LINE_PAY_CONFIRM_URL: str = "http://localhost:5173/checkout/confirm"
    LINE_PAY_CANCEL_URL: str = "http://localhost:5173/checkout/cancel"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    # ECPay
    ECPAY_MERCHANT_ID: str = "2000132"
    ECPAY_HASH_KEY: str = "5294y06JbISpM5x9"
    ECPAY_HASH_IV: str = "v77hoKGq4kWxNNIS"
    ECPAY_IS_SANDBOX: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    ADMIN_URL: str = "http://localhost:5174"

    @property
    def cors_origins(self) -> List[str]:
        return [self.FRONTEND_URL, self.ADMIN_URL]

    @property
    def line_pay_base_url(self) -> str:
        if self.LINE_PAY_IS_SANDBOX:
            return "https://sandbox-api-pay.line.me"
        return "https://api-pay.line.me"

    @property
    def ecpay_logistics_url(self) -> str:
        if self.ECPAY_IS_SANDBOX:
            return "https://logistics-stage.ecpay.com.tw/Express"
        return "https://logistics.ecpay.com.tw/Express"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
