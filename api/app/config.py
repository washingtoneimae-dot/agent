from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://agentmarket:change_me@localhost:5432/agentmarket"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "agentmarket"
    minio_secret_key: str = "change_me"
    minio_bucket: str = "agentmarket-files"
    minio_secure: bool = False
    openrouter_api_key: Optional[str] = ""
    ai_provider: str = "openrouter"
    domain: str = "localhost"
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
