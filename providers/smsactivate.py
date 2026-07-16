import httpx
from typing import Any, Dict
from .base import BaseProvider


class SMSActivateProvider(BaseProvider):
    name = "smsactivate"
    base_url = "https://sms-activate.ru/stubs/handler_api.php"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _build_url(self, params: Dict[str, str]) -> str:
        params["api_key"] = self.api_key
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{query}"

    async def get_balance(self) -> Dict[str, Any]:
        url = self._build_url({"action": "getBalance"})
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text.strip()
            # Обычно приходит "ACCESS_BALANCE:123.45"
            if text.startswith("ACCESS_BALANCE:"):
                balance = float(text.split(":")[1])
                return {"balance": balance, "currency": "RUB", "raw": text}
            return {"error": text, "raw": text}

    async def buy_number(
        self, 
        country: str = "usa", 
        service: str = "telegram", 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Для SMS-Activate country может быть строкой 'usa' или числовым кодом.
        Попробуем сначала строкой. Если не сработает — поменяй на numeric.
        """
        params = {
            "action": "getNumber",
            "service": service,
            "country": country,           # 'usa' или '12' / '187'
            "forward": "0"
        }
        url = self._build_url(params)
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text.strip()
            
            if text.startswith("ACCESS_NUMBER:"):
                # Формат: ACCESS_NUMBER:activation_id:phone
                parts = text.split(":")
                activation_id = parts[1]
                phone = parts[2]
                return {
                    "activation_id": activation_id,
                    "phone": f"+{phone}" if not phone.startswith("+") else phone,
                    "price": None,  # SMS-Activate обычно не возвращает цену сразу
                    "country": country,
                    "service": service,
                    "raw": text
                }
            else:
                return {"error": text, "raw": text}

    async def get_status(self, activation_id: str) -> Dict[str, Any]:
        url = self._build_url({
            "action": "getStatus",
            "id": activation_id
        })
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text.strip()
            
            if text.startswith("STATUS_OK:"):
                sms = text.split(":", 1)[1]
                return {
                    "activation_id": activation_id,
                    "status": "OK",
                    "sms": sms,
                    "raw": text
                }
            elif text == "STATUS_WAIT_CODE":
                return {
                    "activation_id": activation_id,
                    "status": "WAIT_CODE",
                    "sms": None,
                    "raw": text
                }
            else:
                return {"status": text, "raw": text}

    async def set_status(self, activation_id: str, status: str) -> Dict[str, Any]:
        action_map = {
            "OK": "setStatus&status=6",      # 6 = Finish (успешно)
            "Cancel": "setStatus&status=8",  # 8 = Cancel
            "Retry": "setStatus&status=3"    # 3 = Retry
        }
        
        action_part = action_map.get(status, "setStatus&status=8")
        url = self._build_url({
            "action": action_part.split("&")[0],
            "id": activation_id,
            "status": action_part.split("=")[1] if "=" in action_part else "8"
        })
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text.strip()
            return {"success": "ACCESS" in text, "raw": text}
