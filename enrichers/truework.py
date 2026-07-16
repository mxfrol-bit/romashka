from .template import NewServiceEnricher

class TrueworkEnricher(NewServiceEnricher):
    name = "truework"
    # Здесь нужно реализовать реальный API Truework
    # https://www.truework.com/ имеет публичный API для верификации
