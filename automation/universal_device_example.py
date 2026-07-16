"""
Пример использования универсального интерфейса DeviceProvider
=============================================================

Теперь можно легко переключаться между физической и облачной фермой одной строкой.
"""

import asyncio
from cloud_devices.base import BaseDeviceProvider
from cloud_devices.vmos import VMOSCloudProvider
from cloud_devices.physical import PhysicalDeviceProvider


async def run_on_devices(provider: BaseDeviceProvider, device_ids: list):
    """Универсальная функция — работает с любым провайдером"""
    print(f"\n>>> Используем провайдер: {provider.name}")

    # Массовый запуск
    print("Массовый запуск устройств...")
    result = await provider.bulk_start_devices(device_ids)
    print("Результат запуска:", result)

    # Массовое выполнение команды
    print("Выполняем команду на всех устройствах...")
    result = await provider.bulk_execute_command(device_ids, "shell getprop ro.build.version.release")
    print("Результат команды:", result)

    # Останавливаем устройства
    print("Останавливаем устройства...")
    await provider.bulk_stop_devices(device_ids)

    print("Готово!\n")


async def main():
    # ===================== ВЫБОР ПРОВАЙДЕРА =====================
    # Просто поменяй эту переменную, чтобы переключиться между фермами
    USE_CLOUD = True   # True = VMOS Cloud, False = Физическая ферма
    # ============================================================

    if USE_CLOUD:
        provider = VMOSCloudProvider(api_token="твой_vmos_api_token_здесь")
        # Получи реальные device_id через provider.list_devices()
        device_ids = ["vmos_device_id_1", "vmos_device_id_2"]
    else:
        provider = PhysicalDeviceProvider()
        # Здесь будут ID твоих физических устройств (из adb devices)
        device_ids = ["R5CR1234ABC", "R5CR5678DEF"]

    await run_on_devices(provider, device_ids)


if __name__ == "__main__":
    asyncio.run(main())
