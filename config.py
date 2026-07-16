from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    fivesim_api_key: Optional[str] = None
    smsactivate_api_key: Optional[str] = None
    
    default_provider: str = "fivesim"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
