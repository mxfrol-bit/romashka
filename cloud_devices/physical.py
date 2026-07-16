"""
PhysicalDeviceProvider — работа с реальными телефонами через uiautomator2 + ADB

Установка:
    pip install uiautomator2

Перед использованием:
    adb devices
    python -m uiautomator2 init
"""

from typing import List, Dict, Any
import subprocess
from .base import BaseDeviceProvider

# uiautomator2 импортируется только когда реально нужен (ленивый импорт)
# Чтобы не падал проект, если библиотека не установлена
try:
    import uiautomator2 as u2
except ImportError:
    u2 = None


class PhysicalDeviceProvider(BaseDeviceProvider):
    name = "physical_farm"

    def __init__(self):
        pass

    async def list_devices(self) -> List[Dict[str, Any]]:
        """Получить список подключенных устройств"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split("\n")[1:]
            devices = []
            for line in lines:
                if "\t" in line:
                    device_id, status = line.split("\t")
                    devices.append({
                        "id": device_id.strip(),
                        "status": status.strip(),
                        "name": device_id.strip()
                    })
            return devices
        except Exception as e:
            print(f"[Physical] Ошибка list_devices: {e}")
            return []

    async def create_device(self, name: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Невозможно создать физическое устройство")

    async def start_device(self, device_id: str) -> bool:
        return True  # Физические устройства обычно уже включены

    async def stop_device(self, device_id: str) -> bool:
        return False

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        devices = await self.list_devices()
        for d in devices:
            if d["id"] == device_id:
                return d
        return {"id": device_id, "status": "offline"}

    async def execute_command(self, device_id: str, command: str) -> Dict[str, Any]:
        """Выполнить shell команду через ADB"""
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", command],
                capture_output=True, text=True, timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def open_app(self, device_id: str, package_name: str) -> bool:
        """Открыть приложение"""
        try:
            d = u2.connect(device_id)
            d.app_start(package_name)
            return True
        except Exception as e:
            print(f"[Physical] Ошибка open_app: {e}")
            return False

    async def install_app(self, device_id: str, apk_path: str) -> bool:
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "install", "-r", apk_path],
                capture_output=True, text=True, timeout=120
            )
            return "Success" in result.stdout
        except Exception as e:
            print(f"[Physical] Ошибка install_app: {e}")
            return False

    async def execute_uiautomator_action(self, device_id: str, action: dict) -> bool:
        """
        Выполнить действие через uiautomator2.
        Пример:
            {"action": "click", "text": "Войти"}
            {"action": "set_text", "resourceId": "com.app:id/phone", "text": "+1234567890"}
        """
        try:
            d = u2.connect(device_id)
            if action.get("action") == "click":
                if "text" in action:
                    d(text=action["text"]).click()
                elif "resourceId" in action:
                    d(resourceId=action["resourceId"]).click()
            elif action.get("action") == "set_text":
                d(resourceId=action["resourceId"]).set_text(action.get("text", ""))
            return True
        except Exception as e:
            print(f"[Physical] Ошибка uiautomator_action: {e}")
            return False
