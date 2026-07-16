from pydantic_settings import BaseSettings
from typing import Optional, Literal
import logging


class Settings(BaseSettings):
    # PVA Providers (phone number buying)
    fivesim_api_key: Optional[str] = None
    smsactivate_api_key: Optional[str] = None
    default_pva_provider: str = "fivesim"

    # Device Provider settings (phone farm)
    device_provider: Literal["vmos", "physical"] = "vmos"
    vmos_api_token: Optional[str] = None
    physical_adb_host: str = "localhost"

    # General
    port: int = 8000
    log_level: str = "INFO"
    environment: str = "development"  # development / production

    # Security (for Basic Auth in dev)
    basic_auth_username: str = "admin"
    basic_auth_password: str = "admin123"  # Change in production!

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Setup logging professionally
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("usa_farm")
logger.info(f"Settings loaded. Environment: {settings.environment}, Device Provider: {settings.device_provider}")
