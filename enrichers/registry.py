"""
Registry для всех обогатителей данных (enrichers).

Позволяет легко добавлять новые сервисы из твоего списка (Checkr, Truework, Sterling, BeenVerified и т.д.).

Как добавить новый сервис:
1. Создай файл enrichers/название_сервиса.py
2. Наследуй от BaseEnricher
3. Зарегистрируй его здесь в ENRICHERS
"""

from typing import Dict, Type
from .base import BaseEnricher

# Импорты конкретных реализаций
from .example_truepeople import ExampleTruePeopleEnricher

# === РЕЕСТР ВСЕХ ДОСТУПНЫХ ОБОГАТИТЕЛЕЙ ===
ENRICHERS: Dict[str, Type[BaseEnricher]] = {
    "example_truepeople": ExampleTruePeopleEnricher,
    
    # === Сюда добавляй новые сервисы из списка ===
    # "truework": TrueworkEnricher,
    # "checkr": CheckrEnricher,
    # "sterling": SterlingEnricher,
    # "beenverified": BeenVerifiedEnricher,
    # "spokeo": SpokeoEnricher,
    # и т.д.
}


def get_enricher(name: str, **kwargs) -> BaseEnricher:
    """Получить экземпляр обогатителя по имени"""
    if name not in ENRICHERS:
        raise ValueError(f"Enricher '{name}' не найден. Доступные: {list(ENRICHERS.keys())}")
    
    enricher_class = ENRICHERS[name]
    return enricher_class(**kwargs)


def list_available_enrichers() -> list:
    return list(ENRICHERS.keys())
