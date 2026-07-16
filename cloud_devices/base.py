"""
Базовый интерфейс для работы с устройствами (физическими или облачными).

Это позволяет легко переключаться между:
- Физической фермой (uiautomator2 / ADB)
- Облачными устройствами (VMOS, DuoPlus, BitCloudPhone и т.д.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseDeviceProvider(ABC):
    """
    Абстрактный базовый класс для провайдеров устройств.
    Все облачные и физические провайдеры должны наследоваться от него.
    """

    name: str = "base"

    @abstractmethod
    async def list_devices(self) -> List[Dict[str, Any]]:
        """Получить список всех доступных устройств"""
        pass

    @abstractmethod
    async def create_device(self, name: str, **kwargs) -> Dict[str, Any]:
        """Создать новое устройство"""
        pass

    @abstractmethod
    async def start_device(self, device_id: str) -> bool:
        """Запустить устройство"""
        pass

    @abstractmethod
    async def stop_device(self, device_id: str) -> bool:
        """Остановить устройство"""
        pass

    @abstractmethod
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Получить статус устройства"""
        pass

    # ==================== МАССОВЫЕ ОПЕРАЦИИ ====================

    async def bulk_start_devices(self, device_ids: List[str]) -> Dict[str, Any]:
        """Массовый запуск устройств (по умолчанию вызывает start_device по одному)"""
        results = []
        for device_id in device_ids:
            success = await self.start_device(device_id)
            results.append({"device_id": device_id, "success": success})
        return {"results": results}

    async def bulk_stop_devices(self, device_ids: List[str]) -> Dict[str, Any]:
        """Массовый останов устройств"""
        results = []
        for device_id in device_ids:
            success = await self.stop_device(device_id)
            results.append({"device_id": device_id, "success": success})
        return {"results": results}

    async def bulk_execute_command(self, device_ids: List[str], command: str) -> Dict[str, Any]:
        """Массовое выполнение команды (по умолчанию не реализовано)"""
        raise NotImplementedError("bulk_execute_command не реализован в этом провайдере")

    # ==================== УПРАВЛЕНИЕ ПРИЛОЖЕНИЯМИ ====================

    async def install_app(self, device_id: str, apk_url: str) -> bool:
        """Установить приложение"""
        raise NotImplementedError("install_app не реализован")

    async def open_app(self, device_id: str, package_name: str) -> bool:
        """Открыть приложение"""
        raise NotImplementedError("open_app не реализован")

    async def execute_command(self, device_id: str, command: str) -> Dict[str, Any]:
        """Выполнить команду на устройстве"""
        raise NotImplementedError("execute_command не реализован")
