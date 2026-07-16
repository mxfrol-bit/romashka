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

# Безопасный default (исправлено)
safe_default = [name for name in ENRICHER_NAMES if name in available_enrichers]

selected_enrichers = st.sidebar.multiselect(
    "Выбери обогатители данных (сервисы)",
    options=available_enrichers,
    default=safe_default or available_enrichers[:3],
    help="Можно выбрать несколько. Система будет пробовать их по очереди."
)

strategy = st.sidebar.selectbox(
    "Стратегия обогащения",
    options=["first_success", "merge"],
    index=0,
    help="first_success = берём данные из первого успешного сервиса\nmerge = собираем данные из всех"
)

do_buy = st.sidebar.checkbox("Сразу купить одобренные номера через PVA", value=False)

if do_buy:
    pva_service = st.sidebar.selectbox("Какой сервис активировать", ["telegram", "whatsapp", "instagram", "google"])

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

if phones:
    with st.expander("Посмотреть первые 10 номеров"):
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

            try:
                import automation.full_pipeline as fp
                fp.ENRICHER_NAMES = selected_enrichers
                fp.ENRICHER_STRATEGY = strategy

                results = asyncio.run(
                    full_pipeline(
                        input_phones=phones,
                        do_buy=do_buy,
                        service=pva_service if do_buy else "telegram"
                    )
                )

                progress_bar.progress(100)
                status_text.success("Обработка завершена!")

                if results:
                    df = pd.DataFrame(results)

                    st.header("📊 Результаты")
                    st.dataframe(df, use_container_width=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Всего обработано", len(results))
                    with col2:
                        enriched = len([r for r in results if r.get("has_data")])
                        st.metric("С данными", enriched)
                    with col3:
                        if do_buy:
                            bought = len([r for r in results if r.get("bought")])
                            st.metric("Куплено", bought)

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
                status_text.error(f"Ошибка: {str(e)}")
                st.exception(e)

# === Инструкция ===
with st.expander("📖 Как пользоваться"):
    st.markdown("""
    1. Загрузи файл с номерами
    2. Выбери нужные чекеры в боковой панели
    3. Нажми большую кнопку запуска
    4. Скачай результат
    """)

st.markdown("---")
st.caption("USA Number Farm v2 • Streamlit + MultiEnricher")
