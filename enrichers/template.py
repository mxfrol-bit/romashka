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
        
        Сейчас — ДЕМО режим: если нет API ключа, возвращаем правдоподобные тестовые данные по USA.
        Когда будет ключ — замени на реальный запрос + парсинг.
        """
        if not self.api_key:
            print(f"[{self.name}] API key не задан — работаем в ДЕМО-режиме с тестовыми USA данными")

        # === ДЕМО ДАННЫЕ ДЛЯ USA (разные в зависимости от номера) ===
        # В реальности здесь будет настоящий API / скрапинг TruePeople, Intelius и т.д.
        last_digit = phone[-1] if phone else "0"
        
        demo_data_map = {
            "0": {"first_name": "Michael", "last_name": "Johnson", "city": "Los Angeles", "state": "CA", "address": "123 Main St", "zip": "90001"},
            "1": {"first_name": "Jennifer", "last_name": "Smith", "city": "New York", "state": "NY", "address": "456 Broadway Ave", "zip": "10001"},
            "2": {"first_name": "Robert", "last_name": "Williams", "city": "Chicago", "state": "IL", "address": "789 Michigan Ave", "zip": "60601"},
            "3": {"first_name": "Amanda", "last_name": "Brown", "city": "Houston", "state": "TX", "address": "321 Texas Blvd", "zip": "77001"},
            "4": {"first_name": "David", "last_name": "Miller", "city": "Phoenix", "state": "AZ", "address": "654 Desert Rd", "zip": "85001"},
            "5": {"first_name": "Jessica", "last_name": "Davis", "city": "Philadelphia", "state": "PA", "address": "987 Liberty St", "zip": "19101"},
            "6": {"first_name": "James", "last_name": "Wilson", "city": "San Antonio", "state": "TX", "address": "147 River Walk", "zip": "78201"},
            "7": {"first_name": "Sarah", "last_name": "Moore", "city": "San Diego", "state": "CA", "address": "258 Ocean Blvd", "zip": "92101"},
            "8": {"first_name": "Christopher", "last_name": "Taylor", "city": "Dallas", "state": "TX", "address": "369 Dallas Pkwy", "zip": "75201"},
            "9": {"first_name": "Emily", "last_name": "Anderson", "city": "San Jose", "state": "CA", "address": "741 Tech Dr", "zip": "95101"},
        }
        
        data = demo_data_map.get(last_digit, demo_data_map["0"])
        
        return {
            "phone": phone,
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "full_name": f"{data['first_name']} {data['last_name']}",
            "address": data["address"],
            "city": data["city"],
            "state": data["state"],
            "zip": data["zip"],
            "has_data": True,
            "source": self.name,
            "note": "ДЕМО ДАННЫЕ — для реальной работы реализуй API/скрапинг"
        }
