"""
DeviceProviderFactory
=====================

Простая фабрика для получения нужного провайдера устройств.
Это позволяет централизованно управлять, какую ферму использовать.
"""

from typing import Optional
import logging
from .base import BaseDeviceProvider
from .vmos import VMOSCloudProvider
from .physical import PhysicalDeviceProvider

from config import settings

logger = logging.getLogger(__name__)


def get_device_provider(
    provider_type: Optional[str] = None,
    vmos_token: Optional[str] = None
) -> BaseDeviceProvider:
    """
    Возвращает нужный провайдер устройств.
    Использует настройки из config если не указано явно.
    Это позволяет легко переключать ферму через .env или settings.
    """
    if provider_type is None:
        provider_type = settings.device_provider

    provider_type = provider_type.lower()
    logger.info(f"Getting device provider: {provider_type}")

    if provider_type == "vmos":
        token = vmos_token or settings.vmos_api_token
        if not token:
            raise ValueError("VMOS API token is required. Set VMOS_API_TOKEN in .env or pass it.")
        return VMOSCloudProvider(api_token=token)

    elif provider_type == "physical":
        return PhysicalDeviceProvider(adb_host=settings.physical_adb_host)

    else:
        raise ValueError(f"Unknown device provider: {provider_type}. Available: 'vmos', 'physical'")
