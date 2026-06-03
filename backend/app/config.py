from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TW-US Stock Prediction API"
    database_url: str = "postgresql+psycopg://stock_app:stock_app_password@localhost:5432/stock_prediction"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: Optional[str] = None
    llm_provider: str = "openai"
    newsapi_key: Optional[str] = None
    fmp_api_key: Optional[str] = None
    financial_modeling_prep_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    sec_edgar_user_agent: Optional[str] = None
    enable_keyed_market_data: bool = False
    enable_commercial_data_providers: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
