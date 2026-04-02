from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class StripeSettings(BaseSettings):
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRODUCT_ID: str
    STRIPE_CENTS_PER_TOKEN: int = 10  # €0.10 per token
    STRIPE_MIN_CUSTOM_TOKENS: int = 10
    STRIPE_MAX_CUSTOM_TOKENS: int = 10000
    STRIPE_CURRENCY: str = "eur"
    STRIPE_SUCCESS_URL: str = "http://localhost:3000/payment/success"
    STRIPE_CANCEL_URL: str = "http://localhost:3000/payment/cancel"

    # Pre-defined token packages: {price_id: token_count}
    # Set via env as JSON, e.g. STRIPE_TOKEN_PACKAGES='{"price_abc":100,"price_def":500}'
    STRIPE_TOKEN_PACKAGES: dict[str, int] = {}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_stripe_settings() -> StripeSettings:
    return StripeSettings()
