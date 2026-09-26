from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cheap_model: str = "openai/gpt-6-luna"
    premium_model: str = "openai/gpt-6-sol"
    complexity_threshold: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
