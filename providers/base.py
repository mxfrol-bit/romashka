from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    """
    Абстрактный базовый класс для всех PVA/SMS-активационных провайдеров.
    Реализуй эти методы — и провайдер сразу заработает в API.
    """

    name: str = "base"

    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        """Вернуть текущий баланс"""
        pass

    @abstractmethod
    async def buy_number(
        self, 
        country: str = "usa", 
        service: str = "telegram", 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Купить номер.
        Возвращает минимум: {"activation_id": "...", "phone": "+1...", "price": 0.XX}
        """
        pass

    @abstractmethod
    async def get_status(self, activation_id: str) -> Dict[str, Any]:
        """
        Получить статус активации и SMS (если пришло).
        Обычно: {"status": "OK" или "WAIT_CODE", "sms": "123456" или None}
        """
        pass

    @abstractmethod
    async def set_status(self, activation_id: str, status: str) -> Dict[str, Any]:
        """
        Сменить статус: "OK", "Cancel", "Retry"
        """
        pass

    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Можно переопределять для унификации ответов"""
        return data
