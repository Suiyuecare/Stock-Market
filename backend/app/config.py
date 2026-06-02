from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TW-US Stock Prediction API"
    database_url: str = "postgresql+psycopg://stock_app:stock_app_password@localhost:5432/stock_prediction"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: Optional[str] = None
    llm_provider: str = "openai"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
