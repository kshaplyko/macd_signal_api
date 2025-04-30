# main.py
import pandas as pd
import yfinance as yf
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/signal")
def get_signal(ticker: str = "AAPL"):
    df = yf.download(ticker, period="5d", interval="1h")
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    df["EMA12"] = df["Close"].ewm(span=12).mean()
    df["EMA26"] = df["Close"].ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    df.dropna(inplace=True)

    macd_prev, macd_curr = df["MACD"].iloc[-2:]
    signal_prev, signal_curr = df["Signal"].iloc[-2:]

    if macd_prev < signal_prev and macd_curr > signal_curr:
        action = "long"
    elif macd_prev > signal_prev and macd_curr < signal_curr:
        action = "short"
    else:
        action = "hold"

    return {
        "ticker": ticker,
        "close_price": round(df['Close'].iloc[-1], 2),
        "signal": action
    }