"""
VMOS Cloud Provider
Реализует интерфейс BaseDeviceProvider + массовые операции
"""

from typing import List, Dict, Any, Optional
import httpx
from .base import BaseDeviceProvider


class VMOSCloudProvider(BaseDeviceProvider):
    name = "vmos_cloud"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.vmoscloud.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    # ==================== БАЗОВЫЕ МЕТОДЫ ====================

    async def list_devices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/v1/devices", headers=self.headers)
            response.raise_for_status()
            return response.json().get("data", [])

    async def create_device(self, name: str, **kwargs) -> Dict[str, Any]:
        payload = {"name": name, **kwargs}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def start_device(self, device_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/{device_id}/start", headers=self.headers)
            return response.status_code == 200

    async def stop_device(self, device_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/{device_id}/stop", headers=self.headers)
            return response.status_code == 200

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/v1/devices/{device_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()

    # ==================== МАССОВЫЕ ОПЕРАЦИИ ====================

    async def bulk_start_devices(self, device_ids: List[str]) -> Dict[str, Any]:
        """Массовый запуск устройств (использует нативный bulk-эндпоинт VMOS)"""
        payload = {"device_ids": device_ids}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/bulk/start", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def bulk_stop_devices(self, device_ids: List[str]) -> Dict[str, Any]:
        payload = {"device_ids": device_ids}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/bulk/stop", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def bulk_execute_command(self, device_ids: List[str], command: str) -> Dict[str, Any]:
        """Массовое выполнение ADB команды"""
        payload = {"device_ids": device_ids, "command": command}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/bulk/adb", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    # ==================== УПРАВЛЕНИЕ УСТРОЙСТВОМ ====================

    async def execute_command(self, device_id: str, command: str) -> Dict[str, Any]:
        """Выполнить ADB команду на одном устройстве"""
        payload = {"command": command}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/devices/{device_id}/adb", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def open_app(self, device_id: str, package_name: str) -> bool:
        command = f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        result = await self.execute_command(device_id, command)
        return result.get("success", False)
