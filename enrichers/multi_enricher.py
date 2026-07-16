from typing import List, Dict, Any, Optional
from .base import BaseEnricher
from .registry import get_enricher


class MultiEnricher(BaseEnricher):
    """
    Универсальный обогатитель, который может использовать несколько сервисов.
    
    Стратегии:
    - 'first_success': берёт данные из первого сервиса, который вернул результат
    - 'merge': собирает данные из всех сервисов и мёржит
    - 'parallel': запускает все параллельно (быстрее)
    """

    name = "multi"

    def __init__(
        self,
        enricher_names: List[str],
        strategy: str = "first_success",
        **kwargs
    ):
        self.enricher_names = enricher_names
        self.strategy = strategy
        self.kwargs = kwargs

    async def enrich_number(self, phone: str) -> Optional[Dict[str, Any]]:
        results = []

        for name in self.enricher_names:
            try:
                enricher = get_enricher(name, **self.kwargs)
                data = await enricher.enrich_number(phone)
                if data:
                    results.append(data)
                    if self.strategy == "first_success":
                        return data
            except Exception as e:
                print(f"[MultiEnricher] Ошибка в {name}: {e}")
                continue

        if not results:
            return None

        if self.strategy == "merge":
            # Простой мёрдж (можно улучшить)
            merged = {"phone": phone, "sources": []}
            for r in results:
                merged["sources"].append(r.get("source", "unknown"))
                for k, v in r.items():
                    if k not in merged or not merged.get(k):
                        merged[k] = v
            return merged

        return results[0]  # fallback
