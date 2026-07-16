from .template import NewServiceEnricher

class CheckrEnricher(NewServiceEnricher):
    name = "checkr"
    # Checkr имеет хороший публичный API (docs.checkr.com)
