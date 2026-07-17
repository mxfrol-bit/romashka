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

# === Импорты ВСЕХ обогатителей (готовы к использованию в UI) ===
from .example_truepeople import ExampleTruePeopleEnricher
from .truepeople import TruePeopleEnricher
from .beenverified import BeenVerifiedEnricher
from .truthfinder import TruthFinderEnricher
from .instant_checkmate import InstantCheckmateEnricher
from .intelius import InteliusEnricher
from .spokeo import SpokeoEnricher
from .checkr import CheckrEnricher
from .truework import TrueworkEnricher
from .sterling import SterlingEnricher
from .adp_screening import ADPScreeningEnricher
from .certn import CertnEnricher
from .first_advantage import FirstAdvantageEnricher
from .hireright import HireRightEnricher
from .zinc import ZincEnricher

# === РЕЕСТР ВСЕХ ДОСТУПНЫХ ОБОГАТИТЕЛЕЙ ДЛЯ USA (ФИО, адрес, история номера) ===
ENRICHERS: Dict[str, Type[BaseEnricher]] = {
    "example_truepeople": ExampleTruePeopleEnricher,
    "truepeople": TruePeopleEnricher,
    "beenverified": BeenVerifiedEnricher,
    "truthfinder": TruthFinderEnricher,
    "instant_checkmate": InstantCheckmateEnricher,
    "intelius": InteliusEnricher,
    "spokeo": SpokeoEnricher,
    "checkr": CheckrEnricher,
    "truework": TrueworkEnricher,
    "sterling": SterlingEnricher,
    "adp_screening": ADPScreeningEnricher,
    "certn": CertnEnricher,
    "first_advantage": FirstAdvantageEnricher,
    "hireright": HireRightEnricher,
    "zinc": ZincEnricher,
}

# === ДЕМО РЕЖИМ ВКЛЮЧЁН ===
# Все обогатители (truepeople, beenverified, intelius и др.) сейчас возвращают 
# правдоподобные тестовые данные по USA (ФИО, адрес, город, штат).
# Это позволяет сразу тестировать веб-интерфейс, пайплайн и фильтрацию.
#
# Для реальной работы:
# 1. Получи API ключи / доступ к сервисам (TruePeopleSearch, Intelius, BeenVerified, Checkr и т.д.)
# 2. Реализуй настоящий запрос в enrich_number() в файлах enrichers/xxx.py
# 3. Удали "note": "ДЕМО ДАННЫЕ..." из возврата
#
# example_truepeople — отдельный пример с условной логикой (для номеров, заканчивающихся на 0)


def get_enricher(name: str, **kwargs) -> BaseEnricher:
    """Получить экземпляр обогатителя по имени"""
    if name not in ENRICHERS:
        raise ValueError(f"Enricher '{name}' не найден. Доступные: {list(ENRICHERS.keys())}")
    
    enricher_class = ENRICHERS[name]
    return enricher_class(**kwargs)


def list_available_enrichers() -> list:
    return list(ENRICHERS.keys())
