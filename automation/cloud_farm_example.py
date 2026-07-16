"""
ПРИМЕР ИСПОЛЬЗОВАНИЯ ОБЛАЧНЫХ УСТРОЙСТВ (VMOS Cloud)
====================================================

Этот скрипт показывает, как интегрировать облачные телефоны в твой пайплайн.
"""

import asyncio
from cloud_devices.vmos import VMOSCloudProvider


async def main():
    # === НАСТРОЙКИ ===
    VMOS_TOKEN = "твой_api_токен_из_личного_кабинета_vmos"

    provider = VMOSCloudProvider(api_token=VMOS_TOKEN)

    print("=== Получаем список устройств ===")
    devices = await provider.list_devices()
    print(f"Найдено устройств: {len(devices)}")

    if not devices:
        print("Устройств нет. Создаём новое...")
        new_device = await provider.create_device(name="TestFarmDevice")
        print("Создано устройство:", new_device)
        device_id = new_device.get("id")
    else:
        device_id = devices[0]["id"]

    print(f"\n=== Работаем с устройством: {device_id} ===")

    # Запускаем устройство
    print("Запускаем устройство...")
    await provider.start_device(device_id)

    # Ждём, пока устройство загрузится (в реальности нужно polling)
    await asyncio.sleep(15)

    # Пример: открываем приложение Telegram
    print("Открываем Telegram...")
    await provider.open_app(device_id, "org.telegram.messenger")

    # Пример: выполняем ADB команду
    print("Выполняем ADB команду...")
    result = await provider.execute_adb_command(device_id, "shell getprop ro.build.version.release")
    print("Версия Android:", result)

    # Останавливаем устройство
    print("Останавливаем устройство...")
    await provider.stop_device(device_id)

    print("\n✅ Тест завершён успешно!")


if __name__ == "__main__":
    asyncio.run(main())
