from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://agentmarket:change_me@localhost:5432/agentmarket"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    domain: str = "localhost"

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_subscription_price_id: str = "price_placeholder"

    ai_provider: str = "openrouter"
    openrouter_api_key: Optional[str] = ""
    deepseek_api_key: Optional[str] = ""
    openai_api_key: Optional[str] = ""
    ai_model: str = ""

    @property
    def active_ai_config(self) -> dict:
        if self.ai_provider == "deepseek":
            model = self.ai_model or "deepseek-v4-flash"
            return {"provider": "deepseek", "api_key": self.deepseek_api_key or self.openrouter_api_key,
                    "base_url": "https://api.deepseek.com/v1", "model": model}
        elif self.ai_provider == "openai":
            return {"provider": "openai", "api_key": self.openai_api_key or self.openrouter_api_key,
                    "base_url": "https://api.openai.com/v1", "model": self.ai_model or "gpt-4o-mini"}
        else:
            model = self.ai_model or "deepseek/deepseek-v4-flash"
            return {"provider": "openrouter", "api_key": self.openrouter_api_key,
                    "base_url": "https://openrouter.ai/api/v1", "model": model}

    cors_origins_str: str = "http://localhost:3000,http://localhost:80,http://localhost:3001"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_str.split(",") if o.strip()]

    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
