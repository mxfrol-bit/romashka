from .base import BaseDeviceProvider
from typing import List, Dict, Any


class DuoPlusProvider(BaseDeviceProvider):
    name = "duoplus"

    def __init__(self, api_token: str = None):
        self.api_token = api_token

    async def list_devices(self) -> List[Dict[str, Any]]:
        print("[DuoPlus] list_devices (заглушка)")
        return []

    async def create_device(self, name: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("DuoPlusProvider.create_device не реализован")

    async def start_device(self, device_id: str) -> bool:
        print(f"[DuoPlus] start_device {device_id} (заглушка)")
        return True

    async def stop_device(self, device_id: str) -> bool:
        print(f"[DuoPlus] stop_device {device_id} (заглушка)")
        return True

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        return {"id": device_id, "status": "unknown"}
