from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseEnricher(ABC):
    """
    Базовый класс для обогащения номеров данными (ФИО, адрес, и т.д.).
    Реализуй этот класс под свой сервис (TruePeople, аналоги или свой пробив).
    """

    name: str = "base_enricher"

    @abstractmethod
    async def enrich_number(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Обогатить один номер.
        Возвращает словарь с данными или None, если данных нет.
        Пример возврата:
        {
            "phone": "+1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "address": "...",
            "city": "...",
            "state": "CA",
            "has_data": True
        }
        """
        pass

    async def enrich_batch(self, phones: List[str]) -> List[Dict[str, Any]]:
        """Обработать список номеров (можно переопределить для оптимизации)"""
        results = []
        for phone in phones:
            data = await self.enrich_number(phone)
            if data:
                results.append(data)
        return results
