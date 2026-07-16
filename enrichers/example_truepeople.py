import httpx
from typing import Optional, Dict, Any
from .base import BaseEnricher


class ExampleTruePeopleEnricher(BaseEnricher):
    """
    Пример обогатителя под TruePeople / аналогичные сервисы.
    
    В реальной версии замени на свой API ключ и эндпоинты.
    Сейчас это заглушка + пример структуры.
    """

    name = "example_truepeople"

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.truepeople.example.com"  # замени на реальный

    async def enrich_number(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Здесь должен быть реальный запрос к сервису.
        Сейчас возвращает пример данных для демонстрации.
        """
        # === ЗАГЛУШКА ДЛЯ ДЕМО ===
        # В реальности здесь будет:
        # async with httpx.AsyncClient() as client:
        #     r = await client.get(f"{self.base_url}/lookup", params={"phone": phone, "key": self.api_key})
        #     data = r.json()
        #     return { ... }

        # Для примера возвращаем фейковые, но реалистичные данные
        if phone.endswith("0"):  # просто для демо
            return {
                "phone": phone,
                "first_name": "Michael",
                "last_name": "Johnson",
                "full_name": "Michael Johnson",
                "address": "123 Main St",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001",
                "has_data": True,
                "source": "example_truepeople"
            }
        else:
            return None  # нет данных — номер не подходит
