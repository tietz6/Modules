from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "SalesBot API"
    env: str = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> "Settings":
    return Settings()
