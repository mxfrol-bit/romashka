# USA SMS Farm Base — Супер база для работы с USA номерами

Готовый, расширяемый бэкенд для работы с множеством сервисов SMS-активации (PVA) под **USA номера (+1)**.

## Что внутри
- Единый интерфейс для всех провайдеров (легко добавлять новые)
- Поддержка **SMS-Activate** и **5SIM** из коробки (самые стабильные для USA)
- FastAPI приложение — можно деплоить на Railway за 2 минуты
- Простая конфигурация через переменные окружения
- Примеры эндпоинтов: купить номер, получить SMS, сменить статус
- Готово к интеграции с твоим парсером, ботом и скриптом фермы

## Быстрый старт на Railway

1. **Склони репозиторий** или скопируй папку `usa_sms_farm_base` в свой Git-репо.

2. **Зайди на [railway.app](https://railway.app)** → New Project → Deploy from GitHub (или Upload).

3. Railway автоматически увидит Python + FastAPI.

4. **Добавь переменные окружения** в Railway (Settings → Variables):

```env
# Обязательно хотя бы один провайдер
FIVESIM_API_KEY=твой_ключ_5sim
SMSACTIVATE_API_KEY=твой_ключ_sms-activate

# Опционально
DEFAULT_PROVIDER=fivesim          # fivesim или smsactivate
PORT=8000
```

5. Deploy. Получишь публичный URL вида `https://твой-проект.up.railway.app`

Готово! Теперь можно дёргать API с любого места (ферма, бот, парсер).

## Как пользоваться

### Единый API (примеры)

**Купить USA номер под Telegram:**
```bash
curl -X POST "https://твой-url.up.railway.app/buy-number" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "usa",
    "service": "telegram",
    "provider": "fivesim"
  }'
```

**Получить статус / SMS:**
```bash
curl "https://твой-url.up.railway.app/status/123456?provider=fivesim"
```

**Сменить статус (OK / Cancel):**
```bash
curl -X POST "https://твой-url.up.railway.app/set-status" \
  -H "Content-Type: application/json" \
  -d '{"activation_id": "123456", "status": "OK", "provider": "fivesim"}'
```

### В своём коде (Python)

```python
import httpx

BASE_URL = "https://твой-url.up.railway.app"

async def buy_usa_number(service: str = "telegram", provider: str = "fivesim"):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/buy-number", json={
            "country": "usa",
            "service": service,
            "provider": provider
        })
        return r.json()
```

## Как добавить новый провайдер (TextVerified, SMSPool, VoidMob и т.д.)

1. Создай файл `providers/твоё_название.py`
2. Наследуй от `BaseProvider`
3. Реализуй 4 метода:
   - `async def get_balance(self)`
   - `async def buy_number(self, country, service, **kwargs)`
   - `async def get_status(self, activation_id)`
   - `async def set_status(self, activation_id, status)`   # OK / Cancel / Retry

4. Зарегистрируй в `app/main.py` в словаре `PROVIDERS`

Всё — новый провайдер сразу доступен через API.

## Структура проекта

```
usa_sms_farm_base/
├── README.md
├── requirements.txt
├── .env.example
├── config.py
├── app/
│   └── main.py
├── providers/
│   ├── base.py
│   ├── fivesim.py
│   └── smsactivate.py
└── farm_example.py          # пример вызова с фермы
```

## Интеграция с фермой

В скрипте на реальных телефонах (uiautomator2) просто вызывай этот бэкенд:

```python
# В farm_runner.py
number_data = await buy_usa_number(service="instagram", provider="fivesim")
phone = number_data["phone"]
activation_id = number_data["activation_id"]

# ... вводишь phone в приложение ...

sms_code = await get_sms(activation_id, provider="fivesim")
# вводишь код
```

## Следующие шаги (что можно добавить)

- Хранение купленных номеров в БД (Railway Postgres)
- Вебхук при получении SMS
- Массовый бай (batch buy)
- Интеграция с твоим парсером и approval-шагом (ФИО)
- Авто-выбор лучшего провайдера по цене/доступности
- Метрики и дашборд

## 🔥 Полная автоматизация 1 КЛИК (новое)

Теперь в проекте есть мощный пайплайн, который делает всё автоматически:

### Что делает `full_pipeline.py`:

1. Берёт список номеров
2. Прогоняет через **обогащение данными** (ФИО, адрес и т.д. — подключай TruePeople / аналоги)
3. Фильтрует только номера, у которых есть хорошие данные
4. (Опционально) Покупает их через PVA-сервисы
5. Сохраняет результат: **номер + ФИО + данные + статус покупки**

### Как запустить в 1 клик:

```bash
cd usa_sms_farm_base

# Простой прогон (только обогащение + фильтр)
python automation/full_pipeline.py \
    --input my_numbers.txt \
    --output approved_usa_pool.csv

# С автоматической покупкой одобренных номеров
python automation/full_pipeline.py \
    --input my_numbers.txt \
    --output approved_usa_pool.csv \
    --buy \
    --service telegram
```

### Входной файл (`my_numbers.txt`):
```
+12345678901
+12345678902
+12345678903
...
```

### Выходной файл (CSV):
`phone,first_name,last_name,full_name,address,city,state,has_data,bought,activation_id,...`

### Как подключить свой сервис обогащения (TruePeople / аналог):

1. Создай свой класс в `enrichers/твоё_название.py`
2. Наследуй от `BaseEnricher`
3. Реализуй метод `enrich_number(phone)`
4. В `automation/full_pipeline.py` замени строку:
   ```python
   from enrichers.example_truepeople import ExampleTruePeopleEnricher
   ```
   на свой класс.

Готово. Теперь у тебя полностью автоматизированный поток:
**Пул номеров → Проверка ФИО/данных → Фильтр → Покупка → Готовый пул для апрува**

---

## 🌟 Веб-интерфейс (1 клик) — НОВОЕ

Теперь есть красивый веб-интерфейс на Streamlit. Это то, что нужно команде.

### Запуск веб-приложения:

```bash
streamlit run web_app.py
```

Откроется интерфейс в браузере, где можно:
- Загружать файл с номерами
- Выбирать галочками, какие обогатители данных использовать (из твоего списка сервисов)
- Нажимать одну большую кнопку **"Запустить полный пайплайн"**
- Смотреть красивую таблицу результатов
- Скачивать CSV в один клик
- При необходимости сразу покупать одобренные номера

Это уже реальный удобный инструмент, а не просто скрипты.

---

Хочешь, я сделаю ещё круче:
- Добавить историю запусков
- Сделать дашборд статистики
- Добавить больше визуализации (какой сервис лучше работает)
- Развернуть на Railway вместе с бэкендом

## Поддержка

Пиши, если нужно:
- Добавить конкретный сервис из твоего списка (Checkr, Truework, Sterling и т.д.)
- Улучшить веб-интерфейс
- Добавить БД и историю

Теперь ребята действительно могут пользоваться в 1 клик. 🚀
