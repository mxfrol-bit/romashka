"""
ШАБЛОН ДЛЯ СОЗДАНИЯ НОВОГО ОБОГАТИТЕЛЯ
======================================

Скопируй этот файл, переименуй и реализуй метод enrich_number.
"""

from typing import Optional, Dict, Any
from .base import BaseEnricher
import httpx


class NewServiceEnricher(BaseEnricher):
    name = "new_service"

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.newservice.com"  # замени на реальный URL

    async def enrich_number(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Здесь должна быть реальная логика запроса к API сервиса.
        
        Пример структуры:
        - Сделать HTTP запрос
        - Распарсить ответ
        - Вернуть стандартизированный словарь с ФИО, адресом и т.д.
        """
        if not self.api_key:
            print(f"[{self.name}] API key не задан")
            return None

        # Пример запроса (замени на реальный)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                params = {"phone": phone}
                
                # r = await client.get(f"{self.base_url}/v1/lookup", headers=headers, params=params)
                # data = r.json()
                
                # Пример возвращаемых данных:
                return {
                    "phone": phone,
                    "first_name": "John",
                    "last_name": "Doe",
                    "full_name": "John Doe",
                    "address": "123 Main St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "has_data": True,
                    "source": self.name
                }
        except Exception as e:
            print(f"[{self.name}] Ошибка: {e}")
            return None
