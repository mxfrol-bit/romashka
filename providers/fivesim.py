import httpx
from typing import Any, Dict
from .base import BaseProvider


class FiveSimProvider(BaseProvider):
    name = "fivesim"
    base_url = "https://5sim.net"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }

    async def get_balance(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/v1/user/profile", headers=self.headers)
            r.raise_for_status()
            data = r.json()
            return {
                "balance": data.get("balance", 0),
                "currency": "USD",
                "raw": data
            }

    async def buy_number(
        self, 
        country: str = "usa", 
        service: str = "telegram", 
        operator: str = "any",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Пример: country="usa", service="telegram"
        """
        url = f"{self.base_url}/v1/user/buy/activation/{country}/{operator}/{service}"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            r.raise_for_status()
            data = r.json()
            
            return {
                "activation_id": str(data.get("id")),
                "phone": data.get("phone"),
                "price": data.get("price", 0),
                "country": country,
                "service": service,
                "raw": data
            }

    async def get_status(self, activation_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/user/check/{activation_id}"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            r.raise_for_status()
            data = r.json()
            
            sms = data.get("sms")
            status = data.get("status", "UNKNOWN")
            
            return {
                "activation_id": activation_id,
                "status": status,
                "sms": sms if sms else None,
                "raw": data
            }

    async def set_status(self, activation_id: str, status: str) -> Dict[str, Any]:
        """
        Статусы: OK, Cancel, Retry
        """
        url = f"{self.base_url}/v1/user/{status.lower()}/{activation_id}"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            r.raise_for_status()
            data = r.json()
            return {"success": True, "raw": data}
