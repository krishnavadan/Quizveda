from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QuizVeda API"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://quizveda:quizveda@localhost:5432/quizveda"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
