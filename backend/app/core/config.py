"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings, loaded from env vars or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- Application ----------
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_NAME: str = "WhatsApp Business Automation"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    # ---------- Database ----------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/whatsapp_saas"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/whatsapp_saas"

    # ---------- Redis / Celery ----------
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ---------- Security ----------
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Fernet key for encrypting WA access tokens at rest.
    # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # Empty in dev = plaintext fallback. REQUIRED in production.
    ENCRYPTION_KEY: str = ""

    # ---------- Rate limiting ----------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "120/minute"
    RATE_LIMIT_PUBLIC: str = "30/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_WRITE: str = "60/minute"
    RATE_LIMIT_WEBHOOK: str = "2000/minute"

    # ---------- Meta WhatsApp Cloud API (per-business) ----------
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_WEBHOOK_VERIFY_TOKEN: str = ""
    META_GRAPH_API_VERSION: str = "v21.0"
    # Embedded Signup config_id from Meta Business Manager
    META_EMBEDDED_SIGNUP_CONFIG_ID: str = ""

    # ---------- Platform's own WhatsApp number (for OTP/system messages) ----------
    PLATFORM_WHATSAPP_PHONE_NUMBER: str = "+919999999999"
    PLATFORM_WHATSAPP_PHONE_NUMBER_ID: str = ""
    PLATFORM_WHATSAPP_ACCESS_TOKEN: str = ""

    # ---------- Verification ----------
    VERIFICATION_CODE_TTL_MINUTES: int = 10

    # ---------- Razorpay ----------
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # Razorpay plan IDs (created once via Razorpay dashboard / API)
    RAZORPAY_PLAN_ID_STARTER: str = ""
    RAZORPAY_PLAN_ID_GROWTH: str = ""
    RAZORPAY_PLAN_ID_PRO: str = ""
    RAZORPAY_PLAN_ID_AI_ADDON: str = ""

    # ---------- Google Sheets ----------
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "./credentials/google-service-account.json"

    # ---------- Email ----------
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@example.com"

    # ---------- SMS / OTP (fallback only, optional) ----------
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = ""

    # ---------- AI (optional) ----------
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_PROVIDER: Literal["anthropic", "openai"] = "anthropic"
    AI_MODEL: str = "claude-haiku-4-5"

    # ---------- Logging ----------
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    # ---------- Plan limits ----------
    PLAN_STARTER_CONVERSATIONS: int = 1000
    PLAN_GROWTH_CONVERSATIONS: int = 3000
    PLAN_PRO_CONVERSATIONS: int = 6000
    PLAN_AI_REPLIES: int = 1500

    PLAN_STARTER_PRICE_PAISE: int = 39900     # ₹399.00
    PLAN_GROWTH_PRICE_PAISE: int = 99900      # ₹999.00
    PLAN_PRO_PRICE_PAISE: int = 199900        # ₹1999.00
    PLAN_AI_ADDON_PRICE_PAISE: int = 69900    # ₹699.00

    EXTRA_RATE_STARTER_PAISE: int = 60        # ₹0.60
    EXTRA_RATE_GROWTH_PAISE: int = 50         # ₹0.50
    EXTRA_RATE_PRO_PAISE: int = 40            # ₹0.40

    # Trial
    TRIAL_DAYS: int = 14
    TRIAL_CONVERSATIONS: int = 100

    # ---------- GST add-on ("Tax Pack") ----------
    PLAN_TAX_ADDON_PRICE_PAISE: int = 29900   # ₹299
    RAZORPAY_PLAN_ID_TAX_ADDON: str = ""

    # ---------- Cloudflare R2 (invoice PDF storage) ----------
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_ENDPOINT: str = ""           # https://<account>.r2.cloudflarestorage.com
    R2_BUCKET: str = "whatsapp-auto-invoices"
    R2_PUBLIC_BASE: str = ""        # https://invoices.yourdomain.com (custom domain)
    INVOICE_SIGNED_URL_TTL_DAYS: int = 7

    # ---------- SMTP (CA monthly email — falls back to mailhog in dev) ----------
    SMTP_HOST: str = ""
    SMTP_PORT: int = 0
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = False

    # ---------- e-invoice (IRP — V3) ----------
    EINVOICE_USERNAME: str = ""
    EINVOICE_PASSWORD: str = ""
    EINVOICE_CLIENT_ID: str = ""
    EINVOICE_CLIENT_SECRET: str = ""
    EINVOICE_BASE: str = "https://einvapi.charteredinfo.com"   # sandbox
    EINVOICE_GSTIN: str = ""        # platform's own GSTIN

    @model_validator(mode="after")
    def _validate_production_secrets(self):
        """Refuse to boot in production with insecure defaults."""
        if self.APP_ENV != "production":
            return self
        problems: list[str] = []
        if not self.SECRET_KEY or self.SECRET_KEY == "change-me-in-production" or len(self.SECRET_KEY) < 32:
            problems.append("SECRET_KEY must be set to a strong random value (>=32 chars)")
        if not self.ENCRYPTION_KEY:
            problems.append("ENCRYPTION_KEY must be set (Fernet key) — required to encrypt access tokens at rest")
        if not self.META_APP_SECRET:
            problems.append("META_APP_SECRET must be set — webhook signature verification depends on it")
        if not self.META_WEBHOOK_VERIFY_TOKEN:
            problems.append("META_WEBHOOK_VERIFY_TOKEN must be set")
        if not self.RAZORPAY_WEBHOOK_SECRET:
            problems.append("RAZORPAY_WEBHOOK_SECRET must be set — webhook signature verification depends on it")
        if "@postgres:" in self.DATABASE_URL and "sslmode" not in self.DATABASE_URL:
            problems.append("DATABASE_URL should use sslmode=require in production")
        if problems:
            raise RuntimeError(
                "Refusing to start in production with insecure config:\n  - "
                + "\n  - ".join(problems)
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
