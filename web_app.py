"""
КРУТОЙ ВЕБ-ИНТЕРФЕЙС ДЛЯ USA NUMBER FARM
=========================================

1 клик: загрузил номера → выбрал обогатители → нажал "Запустить" → получил результат.

Запуск:
    streamlit run web_app.py
"""

import streamlit as st
import pandas as pd
import asyncio
import sys
from typing import List

sys.path.append(".")

from enrichers.registry import get_enricher, list_available_enrichers
from enrichers.multi_enricher import MultiEnricher
from automation.full_pipeline import full_pipeline, ENRICHER_NAMES, ENRICHER_STRATEGY

st.set_page_config(
    page_title="USA Number Farm",
    page_icon="🇺🇸",
    layout="wide"
)

st.title("🇺🇸 USA Number Farm — 1 Click Tool")
st.markdown("**Проверка пула номеров + обогащение данными + покупка**")

# === SIDEBAR: Настройки ===
st.sidebar.header("⚙️ Настройки")

available_enrichers = list_available_enrichers()

selected_enrichers = st.sidebar.multiselect(
    "Выбери обогатители данных (сервисы)",
    options=available_enrichers,
    default=ENRICHER_NAMES,
    help="Можно выбрать несколько. Система будет пробовать их по очереди."
)

strategy = st.sidebar.selectbox(
    "Стратегия обогащения",
    options=["first_success", "merge"],
    index=0,
    help="first_success = берём данные из первого успешного сервиса\nmerge = собираем данные из всех"
)

do_buy = st.sidebar.checkbox("Покупать одобренные номера через PVA", value=False)
pva_service = st.sidebar.text_input("Какой сервис активировать", value="telegram")

backend_url = st.sidebar.text_input(
    "Backend URL (Railway)",
    value="https://твой-проект.up.railway.app"
)

st.sidebar.markdown("---")
st.sidebar.info("Добавляй новые сервисы в `enrichers/registry.py`")

# === Основная часть ===
st.header("1. Загрузи номера")

uploaded_file = st.file_uploader(
    "Загрузи TXT или CSV с номерами (по одному на строку)",
    type=["txt", "csv"]
)

phones: List[str] = []

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    phones = [line.strip() for line in content.splitlines() if line.strip()]
    st.success(f"Загружено {len(phones)} номеров")

# Показать превью
if phones:
    st.write("Первые 10 номеров:")
    st.code("\n".join(phones[:10]))

# === Кнопка запуска ===
st.header("2. Запусти обработку")

if st.button("🚀 Запустить полный пайплайн (1 клик)", type="primary", disabled=len(phones) == 0):
    if not selected_enrichers:
        st.error("Выбери хотя бы один обогатитель данных")
    else:
        with st.spinner("Обрабатываем номера... Это может занять время"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Обновляем глобальные настройки
            import automation.full_pipeline as fp
            fp.ENRICHER_NAMES = selected_enrichers
            fp.ENRICHER_STRATEGY = strategy
            fp.BACKEND_URL = backend_url

            # Запускаем pipeline
            try:
                results = asyncio.run(
                    full_pipeline(
                        input_phones=phones,
                        do_buy=do_buy,
                        service=pva_service
                    )
                )

                progress_bar.progress(100)
                status_text.success("Обработка завершена!")

                if results:
                    df = pd.DataFrame(results)

                    st.header("📊 Результаты")

                    # Показываем красивую таблицу
                    st.dataframe(df, use_container_width=True)

                    # Статистика
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Всего обработано", len(results))
                    with col2:
                        enriched_count = len([r for r in results if r.get("has_data")])
                        st.metric("С данными (одобрено)", enriched_count)
                    with col3:
                        if do_buy:
                            bought_count = len([r for r in results if r.get("bought")])
                            st.metric("Куплено", bought_count)

                    # Скачивание
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Скачать результат (CSV)",
                        data=csv,
                        file_name="usa_number_farm_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("Не удалось получить данные ни по одному номеру.")

            except Exception as e:
                st.error(f"Ошибка при обработке: {str(e)}")
                st.exception(e)

# === Инструкция ===
with st.expander("📖 Как пользоваться"):
    st.markdown("""
    1. Загрузи файл с номерами (TXT или CSV)
    2. В боковой панели выбери, какие сервисы обогащения использовать
    3. Нажми большую синюю кнопку **"Запустить полный пайплайн"**
    4. Дождись результата и скачай CSV
    5. При необходимости включи опцию покупки номеров
    """)

st.markdown("---")
st.caption("USA Number Farm v2 • Streamlit + MultiEnricher")