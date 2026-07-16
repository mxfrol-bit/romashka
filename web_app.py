import streamlit as st
import pandas as pd
import asyncio
import sys
from typing import List

sys.path.append(".")

from enrichers.registry import list_available_enrichers
from automation.full_pipeline import full_pipeline, ENRICHER_NAMES

st.set_page_config(
    page_title="USA Number Farm",
    page_icon="🇺🇸",
    layout="wide"
)

st.title("🇺🇸 USA Number Farm — 1 Click Tool")
st.markdown("**Проверка пула номеров + обогащение данными + покупка**")

# === SIDEBAR ===
st.sidebar.header("⚙️ Настройки")

available_enrichers = list_available_enrichers()

# === ИСПРАВЛЕНИЕ: безопасный default ===
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
    help="first_success = берём данные из первого успешного\nmerge = собираем данные из всех"
)

do_buy = st.sidebar.checkbox("Сразу купить одобренные номера", value=False)

if do_buy:
    pva_service = st.sidebar.selectbox("Сервис для покупки", ["telegram", "whatsapp", "instagram", "google"])

st.sidebar.markdown("---")

# === ОСНОВНОЙ ИНТЕРФЕЙС ===
st.header("1. Загрузи номера")

uploaded_file = st.file_uploader("TXT или CSV с номерами", type=["txt", "csv"])

phones: List[str] = []
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    phones = [line.strip() for line in content.splitlines() if line.strip()]
    st.success(f"Загружено {len(phones)} номеров")

if phones:
    with st.expander("Первые 10 номеров"):
        st.code("\n".join(phones[:10]))

st.header("2. Запуск")

if st.button("🚀 Запустить", type="primary", disabled=len(phones) == 0):
    if not selected_enrichers:
        st.error("Выбери хотя бы один чекер")
    else:
        with st.spinner("Выполняем проверку..."):
            try:
                import automation.full_pipeline as fp_module
                fp_module.ENRICHER_NAMES = selected_enrichers
                fp_module.ENRICHER_STRATEGY = strategy

                results = asyncio.run(
                    full_pipeline(input_phones=phones, do_buy=do_buy)
                )

                if results:
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Скачать CSV", csv, "results.csv")
                else:
                    st.warning("Нет результатов")

            except Exception as e:
                st.error(f"Ошибка: {e}")
                st.exception(e)

st.caption("USA Number Farm • Чекер + Устройства")
