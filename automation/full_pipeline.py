"""
ПОЛНАЯ АВТОМАТИЗАЦИЯ 1 КЛИК — ИСТОРИЯ НОМЕРА
=============================================

По умолчанию запускаются 5 чекеров для поиска предыдущих владельцев номера:
truepeople, beenverified, truthfinder, instant_checkmate, intelius

Задача:
1. Берём пул номеров
2. Прогоняем через 5 чекеров истории (ФИО предыдущих владельцев, адрес и т.д.)
3. Фильтруем номера, у которых есть исторические данные
4. (Опционально) Покупаем их через PVA
5. Получаем готовый пул: номер + история владельцев

Как запустить:
    python automation/full_pipeline.py --input numbers.txt --output approved_pool.csv

Или через веб-интерфейс: streamlit run web_app.py
"""

import asyncio
import argparse
import csv
import json
from typing import List, Dict, Any
import httpx

# === НАСТРОЙКИ ===
BACKEND_URL = "https://твой-проект.up.railway.app"   # ← замени на свой Railway URL
DEFAULT_PROVIDER = "fivesim"                         # fivesim или smsactivate

# === ИМПОРТЫ ИЗ ПРОЕКТА ===
import sys
sys.path.append("..")

from enrichers.registry import get_enricher, list_available_enrichers
from enrichers.multi_enricher import MultiEnricher

# === НАСТРОЙКА ОБОГАТИТЕЛЕЙ (5 основных чекеров для истории номера) ===
ENRICHER_NAMES = [
    "truepeople",
    "beenverified",
    "truthfinder",
    "instant_checkmate",
    "intelius"
]
ENRICHER_STRATEGY = "first_success"

# === НАСТРОЙКА УСТРОЙСТВ (Device Provider) ===
DEVICE_PROVIDER_TYPE = "vmos"                    # "vmos" или "physical"
VMOS_API_TOKEN = None                            # Заполни токен, если используешь VMOS


async def get_device_provider():
    """Возвращает нужный провайдер устройств"""
    from cloud_devices.factory import get_device_provider as factory_get

    if DEVICE_PROVIDER_TYPE == "vmos":
        if not VMOS_API_TOKEN:
            raise ValueError("Нужно указать VMOS_API_TOKEN")
        return factory_get("vmos", vmos_token=VMOS_API_TOKEN)
    else:
        return factory_get("physical")


async def enrich_numbers(phones: List[str]) -> List[Dict[str, Any]]:
    """Обогащаем номера данными через MultiEnricher"""
    if len(ENRICHER_NAMES) == 1:
        enricher = get_enricher(ENRICHER_NAMES[0])
    else:
        enricher = MultiEnricher(
            enricher_names=ENRICHER_NAMES,
            strategy=ENRICHER_STRATEGY
        )
    
    enriched = await enricher.enrich_batch(phones)
    return enriched


async def buy_number_via_backend(phone: str, service: str = "telegram") -> Dict[str, Any]:
    """Покупаем номер через бэкенд (если нужно)"""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{BACKEND_URL}/buy-number",
            json={
                "country": "usa",
                "service": service,
                "provider": DEFAULT_PROVIDER
            }
        )
        return r.json()


async def full_pipeline(
    input_phones: List[str],
    do_buy: bool = False,
    service: str = "telegram"
) -> List[Dict[str, Any]]:
    """
    Главная функция — полная автоматизация.
    """
    print(f"🔍 Начинаем обогащение {len(input_phones)} номеров...")

    # 1. Обогащаем данные
    enriched_list = await enrich_numbers(input_phones)
    print(f"✅ Обогащено: {len(enriched_list)} номеров имеют данные")

    # 2. Фильтруем только те, у которых есть хорошие данные
    approved = [item for item in enriched_list if item.get("has_data")]

    print(f"🎯 Одобрено после фильтра: {len(approved)}")

    # 3. Опционально покупаем через PVA
    if do_buy:
        print("💰 Покупаем одобренные номера через PVA...")
        for item in approved:
            try:
                buy_result = await buy_number_via_backend(item["phone"], service=service)
                item["bought"] = True
                item["activation_id"] = buy_result.get("activation_id")
                item["buy_price"] = buy_result.get("price")
            except Exception as e:
                item["bought"] = False
                item["error"] = str(e)
        print("✅ Покупка завершена")

    return approved


def save_results(results: List[Dict[str, Any]], output_path: str):
    """Сохраняем результат в CSV"""
    if not results:
        print("Нет данных для сохранения.")
        return

    keys = results[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"💾 Результат сохранён: {output_path}")


async def main():
    parser = argparse.ArgumentParser(description="Полная автоматизация пула USA номеров + обогащение данными")
    parser.add_argument("--input", required=True, help="Файл со списком номеров (по одному на строку)")
    parser.add_argument("--output", default="approved_pool.csv", help="Куда сохранить результат")
    parser.add_argument("--buy", action="store_true", help="Покупать номера через PVA после фильтра")
    parser.add_argument("--service", default="telegram", help="Какой сервис активировать (для PVA)")
    parser.add_argument("--list-enrichers", action="store_true", help="Показать доступные обогатители данных")

    args = parser.parse_args()

    if args.list_enrichers:
        print("Доступные обогатители данных:")
        print(list_available_enrichers())
        return

    # Читаем номера
    with open(args.input, "r") as f:
        phones = [line.strip() for line in f if line.strip()]

    print(f"📥 Загружено {len(phones)} номеров из {args.input}")
    print(f"🔧 Используемые обогатители: {ENRICHER_NAMES} (стратегия: {ENRICHER_STRATEGY})")

    # Запускаем полную автоматизацию
    results = await full_pipeline(
        input_phones=phones,
        do_buy=args.buy,
        service=args.service
    )

    # Сохраняем
    save_results(results, args.output)

    print("\n🎉 Готово! 1 клик выполнен.")


if __name__ == "__main__":
    asyncio.run(main())
