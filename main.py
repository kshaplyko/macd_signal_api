from fastapi import FastAPI, Query
import pandas as pd, yfinance as yf, time, json, os

app = FastAPI()
LOG_FILE = "trades.json"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f: json.dump([], f)

def save(trade: dict):
    with open(LOG_FILE, "r+") as f:
        data = json.load(f); data.append(trade)
        f.seek(0); json.dump(data, f, indent=2)

def macd_action(df: pd.DataFrame) -> str:
    df["ema12"] = df.Close.ewm(span=12).mean()
    df["ema26"] = df.Close.ewm(span=26).mean()
    df["macd"]  = df.ema12 - df.ema26
    df["sig"]   = df.macd.ewm(span=9).mean()
    m_prev, m_now = df.macd.iloc[-2:]
    s_prev, s_now = df.sig .iloc[-2:]
    if m_prev < s_prev and m_now > s_now: return "long"
    if m_prev > s_prev and m_now < s_now: return "short"
    return "hold"

@app.get("/")
def root(): return {"status": "ok"}

@app.get("/signal")
def signal(ticker: str = Query("AAPL"), interval: str = Query("1h")):
    df = yf.download(ticker, period="14d", interval=interval)[["Close"]].dropna()
    if len(df) < 30: return {"error":"few-data"}
    action = macd_action(df)
    trade = {"ts": int(time.time()), "ticker": ticker,
             "price": float(df.Close.iloc[-1]), "signal": action}
    save(trade)
    return trade

@app.get("/trades")
def trades():
    with open(LOG_FILE) as f: return json.load(f)