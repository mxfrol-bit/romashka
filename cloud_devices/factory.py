"""
DeviceProviderFactory
=====================

Простая фабрика для получения нужного провайдера устройств.
Это позволяет централизованно управлять, какую ферму использовать.
"""

from typing import Optional
from .base import BaseDeviceProvider
from .vmos import VMOSCloudProvider
from .physical import PhysicalDeviceProvider


def get_device_provider(
    provider_type: str = "vmos",
    vmos_token: Optional[str] = None
) -> BaseDeviceProvider:
    """
    Возвращает нужный провайдер устройств.

    Args:
        provider_type: "vmos" или "physical"
        vmos_token: API токен для VMOS (обязателен, если provider_type="vmos")
    """
    provider_type = provider_type.lower()

    if provider_type == "vmos":
        if not vmos_token:
            raise ValueError("Для VMOS Cloud нужно передать vmos_token")
        return VMOSCloudProvider(api_token=vmos_token)

    elif provider_type == "physical":
        return PhysicalDeviceProvider()

    else:
        raise ValueError(f"Неизвестный тип провайдера: {provider_type}. "
                         f"Доступно: 'vmos', 'physical'")
