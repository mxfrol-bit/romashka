# USA Number Farm — Карта проекта (для разработчика)

## 1. Общая архитектура

Проект представляет собой **гибридную систему** для работы с номерами и устройствами:

```
┌─────────────────────────────────────────────────────────────────┐
│                        ВЕБ-ИНТЕРФЕЙС                              │
│   (Streamlit + HTML)                                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
│   - PVA провайдеры (5SIM, SMS-Activate)                         │
│   - Облачные устройства (VMOS, ...)                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Чекеры данных  │   │  Облачные       │   │  Физическая     │
│  (история       │   │  устройства     │   │  ферма          │
│   номера)       │   │  (VMOS и др.)   │   │  (заглушка)     │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 2. Структура проекта

```
usa_sms_farm_base/
├── README.md
├── CLOUD_PHONE_MIGRATION_PLAN.md     ← План миграции на облако
├── PROJECT_MAP.md                    ← Эта карта проекта
│
├── requirements.txt
├── Dockerfile
├── railway.json
│
├── app/
│   └── main.py                       ← FastAPI бэкенд + Basic Auth
│
├── frontend/
│   └── index.html                    ← Отдельный HTML-интерфейс
│
├── web_app.py                        ← Streamlit веб-интерфейс
│
├── config.py
├── .env.example
│
├── automation/                       ← Основная бизнес-логика
│   ├── full_pipeline.py              ← Главный пайплайн (чекеры + устройства)
│   ├── cloud_farm_example.py
│   └── universal_device_example.py   ← Пример переключения между фермами
│
├── cloud_devices/                    ← Универсальная система устройств
│   ├── base.py                       ← Абстрактный интерфейс BaseDeviceProvider
│   ├── vmos.py                       ← Реализация под VMOS Cloud + bulk-методы
│   ├── physical.py                   ← Заглушка для физической фермы
│   └── (duoplus.py, bitcloudphone.py — в будущем)
│
├── enrichers/                        ← Система проверки данных (история номера)
│   ├── base.py
│   ├── registry.py                   ← Реестр всех чекеров
│   ├── multi_enricher.py
│   ├── truepeople.py
│   ├── beenverified.py
│   ├── truthfinder.py
│   ├── instant_checkmate.py
│   ├── intelius.py
│   └── ... (другие из списка)
│
├── providers/                        ← PVA-провайдеры (покупка номеров)
│   ├── base.py
│   ├── fivesim.py
│   └── smsactivate.py
│
└── cloud_devices/                    ← (уже описано выше)
```

## 3. Ключевые абстракции

### 3.1 DeviceProvider (Самая важная абстракция)

```python
class BaseDeviceProvider(ABC):
    async def list_devices()
    async def start_device(device_id)
    async def stop_device(device_id)
    async def bulk_start_devices(device_ids)      # Массовые операции
    async def bulk_execute_command(device_ids, command)
    ...
```

**Реализации:**
- `VMOSCloudProvider` — полностью реализован
- `PhysicalDeviceProvider` — заглушка (готов к реализации)

### 3.2 Enricher (Чекеры данных)

```python
class BaseEnricher(ABC):
    async def enrich_number(phone) -> dict | None
```

**Реестр** находится в `enrichers/registry.py`.

## 4. Текущее состояние проекта

| Компонент                    | Статус          | Примечание |
|-----------------------------|------------------|----------|
| Веб-интерфейс (Streamlit)   | Готов           | Работает |
| HTML-интерфейс              | Готов           | Базовая версия |
| FastAPI бэкенд              | Готов           | + Basic Auth |
| Система чекеров (5 шт.)     | Готов           | truepeople, beenverified и др. |
| Универсальный DeviceProvider| Готов           | `base.py` |
| VMOS Cloud интеграция       | Готов           | + массовые операции |
| PhysicalDeviceProvider      | Заглушка        | Нужно реализовать |
| Полная миграция на облако   | В процессе      | Есть план |
| Поддержка DuoPlus / BitCloudPhone | Не начато | Можно добавить |

## 5. Как переключаться между фермами

```python
# В любом месте кода
from cloud_devices.vmos import VMOSCloudProvider
from cloud_devices.physical import PhysicalDeviceProvider

USE_CLOUD = True

if USE_CLOUD:
    provider = VMOSCloudProvider(api_token=...)
else:
    provider = PhysicalDeviceProvider()
```

## 6. Что нужно сделать дальше (приоритет)

1. Реализовать реальные методы в `PhysicalDeviceProvider` (через `uiautomator2`)
2. Подключить VMOS Cloud к основному пайплайну
3. Добавить поддержку DuoPlus / BitCloudPhone (по необходимости)
4. Улучшить веб-интерфейс под облачные устройства

---

**Готово к передаче разработчику.**  
Всё структурировано, есть абстракции и план миграции.
