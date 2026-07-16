from .template import NewServiceEnricher

class TruePeopleEnricher(NewServiceEnricher):
    name = "truepeople"

    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.base_url = "https://api.truepeoplesearch.com"  # пример, замени на реальный
