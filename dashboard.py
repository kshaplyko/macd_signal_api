import streamlit as st
import pandas as pd
import requests
import datetime as dt

# ← постоянный URL вашего FastAPI-сервиса
API_TRADES = "https://macdsignalapi.kirillshaplyko.repl.co/trades"

st.set_page_config(page_title="MACD-бот • дашборд", layout="wide")
st.title("💹 Учебный MACD-робот — история сигналов")

try:
    data = requests.get(API_TRADES, timeout=10).json()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Не удалось получить данные: {e}")
    st.stop()

if df.empty:
    st.info("Записей пока нет — подождите, пока /signal создаст первую сделку.")
else:
    # преобразуем время
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    df = df.sort_values("time")

    # основной график цены
    st.subheader("Кривая цены (последние сигналы)")
    st.line_chart(df.set_index("time")["price"])

    # таблица последних 20 записей
    st.subheader("Последние сделки / сигналы")
    st.dataframe(
        df[["time", "ticker", "price", "signal"]]
        .tail(20)
        .rename(columns={
            "time": "Время",
            "ticker": "Тикер",
            "price": "Цена",
            "signal": "Сигнал"
        }),
        use_container_width=True
    )