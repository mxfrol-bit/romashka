"""
Пример использования бэкенда из скрипта фермы (uiautomator2 или любой другой).

Просто вызывай эндпоинты своего Railway-деплоя.
"""

import asyncio
import httpx
from typing import Optional

# === ЗАМЕНИ НА СВОЙ URL после деплоя на Railway ===
BACKEND_URL = "https://твой-проект.up.railway.app"


async def buy_usa_number(service: str = "telegram", provider: str = "fivesim") -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{BACKEND_URL}/buy-number",
            json={
                "country": "usa",
                "service": service,
                "provider": provider
            }
        )
        r.raise_for_status()
        return r.json()


async def get_sms(activation_id: str, provider: str = "fivesim") -> Optional[str]:
    """Ждёт SMS до 60 секунд"""
    async with httpx.AsyncClient(timeout=65) as client:
        for _ in range(12):  # 12 попыток по 5 сек
            r = await client.get(
                f"{BACKEND_URL}/status/{activation_id}",
                params={"provider": provider}
            )
            data = r.json()
            if data.get("sms"):
                return data["sms"]
            if data.get("status") == "OK":
                return data.get("sms")
            await asyncio.sleep(5)
    return None


async def finish_activation(activation_id: str, provider: str = "fivesim"):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/set-status",
            json={
                "activation_id": activation_id,
                "status": "OK",
                "provider": provider
            }
        )
        return r.json()


# ==================== ПРИМЕР ИСПОЛЬЗОВАНИЯ В ФЕРМЕ ====================

async def example_farm_flow():
    print("Покупаем USA номер под Telegram...")
    number_data = await buy_usa_number(service="telegram", provider="fivesim")
    
    print(f"Номер: {number_data['phone']}")
    print(f"ID активации: {number_data['activation_id']}")
    
    # Здесь твой uiautomator2 код:
    # d(resourceId=...).set_text(number_data['phone'])
    # ... жмёшь "Получить код" ...
    
    print("Ждём SMS...")
    sms = await get_sms(number_data["activation_id"], provider="fivesim")
    
    if sms:
        print(f"Получен код: {sms}")
        # d.set_text(sms)
        # ... завершаем регистрацию ...
        
        await finish_activation(number_data["activation_id"], provider="fivesim")
        print("Активация завершена успешно!")
    else:
        print("SMS не пришло, отменяем...")
        # await set_status(..., "Cancel")


if __name__ == "__main__":
    asyncio.run(example_farm_flow())
