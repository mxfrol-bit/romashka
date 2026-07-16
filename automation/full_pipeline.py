"""
ПОЛНЫЙ ПАЙПЛАЙН (Чекер + Устройства)
====================================

Этот файл теперь поддерживает два этапа:
1. Проверка номеров через чекеры (история владельцев)
2. Работа с Android-устройствами (VMOS / Physical)

Можно запускать отдельно или вместе.
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional
from config import settings

# === Импорты ===
from enrichers.registry import get_enricher, list_available_enrichers
from enrichers.multi_enricher import MultiEnricher
from cloud_devices.factory import get_device_provider

# === НАСТРОЙКИ ===
BACKEND_URL = "https://твой-проект.up.railway.app"
DEFAULT_PROVIDER = "fivesim"

# Чекеры (можно менять)
ENRICHER_NAMES = [
    "truepeople",
    "beenverified",
    "truthfinder",
    "instant_checkmate",
    "intelius"
]
ENRICHER_STRATEGY = "first_success"

# Устройства
DEVICE_PROVIDER_TYPE = settings.device_provider
VMOS_API_TOKEN = settings.vmos_api_token


async def get_device_provider_instance():
    """Получаем текущий провайдер устройств"""
    return get_device_provider(
        provider_type=DEVICE_PROVIDER_TYPE,
        vmos_token=VMOS_API_TOKEN
    )


# ==================== ЭТАП 1: ЧЕКЕР ====================

async def enrich_numbers(phones: List[str]) -> List[Dict[str, Any]]:
    """Проверка номеров через чекеры"""
    if not phones:
        return []

    if len(ENRICHER_NAMES) == 1:
        enricher = get_enricher(ENRICHER_NAMES[0])
    else:
        enricher = MultiEnricher(
            enricher_names=ENRICHER_NAMES,
            strategy=ENRICHER_STRATEGY
        )

    results = await enricher.enrich_batch(phones)
    return results


# ==================== ЭТАП 2: РАБОТА С УСТРОЙСТВАМИ ====================

async def run_on_devices(device_ids: List[str], command: str = "shell getprop ro.build.version.release"):
    """Выполнить команду на нескольких устройствах"""
    provider = await get_device_provider_instance()
    return await provider.bulk_execute_command(device_ids, command)


async def start_devices(device_ids: List[str]):
    """Запустить несколько устройств"""
    provider = await get_device_provider_instance()
    return await provider.bulk_start_devices(device_ids)


async def stop_devices(device_ids: List[str]):
    """Остановить несколько устройств"""
    provider = await get_device_provider_instance()
    return await provider.bulk_stop_devices(device_ids)


# ==================== ОБЪЕДИНЁННЫЙ ПАЙПЛАЙН ====================

async def full_pipeline(
    input_phones: List[str],
    do_buy: bool = False,
    service: str = "telegram",
    device_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Полный пайплайн:
    1. Проверка номеров через чекеры
    2. (Опционально) Покупка номеров
    3. (Опционально) Работа на Android-устройствах
    """
    print(f"Запуск пайплайна. Номеров: {len(input_phones)}")

    # Этап 1: Чекер
    enriched = await enrich_numbers(input_phones)
    print(f"После проверки: {len(enriched)} результатов")

    # Этап 2: Покупка (если нужно)
    if do_buy:
        # Здесь можно добавить логику покупки
        print("Покупка номеров включена (реализация в разработке)")

    # Этап 3: Работа на устройствах (если переданы device_ids)
    if device_ids:
        provider = await get_device_provider_instance()
        print(f"Запуск на устройствах: {device_ids}")
        await provider.bulk_start_devices(device_ids)
        # Здесь можно добавить выполнение команд регистрации и т.д.

    return enriched


# ==================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ====================

async def example_usage():
    """Пример использования"""
    test_phones = ["+1234567890", "+1234567891"]

    # Только чекер
    results = await enrich_numbers(test_phones)
    print("Результаты чекера:", results)

    # Полный пайплайн с устройствами
    # results = await full_pipeline(test_phones, device_ids=["device_1", "device_2"])


if __name__ == "__main__":
    asyncio.run(example_usage())
