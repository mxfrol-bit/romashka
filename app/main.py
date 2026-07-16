from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

from config import settings
from providers.base import BaseProvider
from providers.fivesim import FiveSimProvider
from providers.smsactivate import SMSActivateProvider

app = FastAPI(
    title="USA SMS Farm Base",
    description="Унифицированный API для работы с USA номерами через разные PVA-сервисы",
    version="1.0.0"
)

# Разрешаем запросы с фронтенда (HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация провайдеров
PROVIDERS: Dict[str, BaseProvider] = {}

def get_provider(name: Optional[str] = None) -> BaseProvider:
    provider_name = name or settings.default_provider
    
    if provider_name not in PROVIDERS:
        if provider_name == "fivesim" and settings.fivesim_api_key:
            PROVIDERS[provider_name] = FiveSimProvider(settings.fivesim_api_key)
        elif provider_name == "smsactivate" and settings.smsactivate_api_key:
            PROVIDERS[provider_name] = SMSActivateProvider(settings.smsactivate_api_key)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Provider '{provider_name}' не настроен или нет API ключа"
            )
    return PROVIDERS[provider_name]


class BuyRequest(BaseModel):
    country: str = "usa"
    service: str = "telegram"
    provider: Optional[str] = None
    operator: Optional[str] = "any"


class StatusRequest(BaseModel):
    activation_id: str
    status: str  # OK, Cancel, Retry
    provider: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    # Предзагружаем провайдеры, у которых есть ключи
    if settings.fivesim_api_key:
        PROVIDERS["fivesim"] = FiveSimProvider(settings.fivesim_api_key)
    if settings.smsactivate_api_key:
        PROVIDERS["smsactivate"] = SMSActivateProvider(settings.smsactivate_api_key)
    print(f"Загружено провайдеров: {list(PROVIDERS.keys())}")


@app.get("/")
async def root():
    return {
        "message": "USA SMS Farm Base is running",
        "available_providers": list(PROVIDERS.keys()),
        "default_provider": settings.default_provider
    }


@app.get("/balance")
async def get_balance(provider: Optional[str] = Query(None)):
    prov = get_provider(provider)
    try:
        return await prov.get_balance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/buy-number")
async def buy_number(req: BuyRequest):
    prov = get_provider(req.provider)
    try:
        result = await prov.buy_number(
            country=req.country,
            service=req.service,
            operator=req.operator or "any"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{activation_id}")
async def get_status(activation_id: str, provider: Optional[str] = Query(None)):
    prov = get_provider(provider)
    try:
        return await prov.get_status(activation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set-status")
async def set_status(req: StatusRequest):
    prov = get_provider(req.provider)
    try:
        return await prov.set_status(req.activation_id, req.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
