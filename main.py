from fastapi import FastAPI, Query
import pandas as pd, yfinance as yf, json, os, time

app = FastAPI()
LOG = "trades.json"
if not os.path.exists(LOG):
    with open(LOG, "w") as f:
        json.dump([], f)

def save_trade(t: dict):
    with open(LOG, "r+") as f:
        data = json.load(f)
        data.append(t)
        f.seek(0); json.dump(data, f, indent=2)

def macd(df: pd.DataFrame) -> str:
    df["ema12"] = df.Close.ewm(span=12).mean()
    df["ema26"] = df.Close.ewm(span=26).mean()
    df["macd"]  = df.ema12 - df.ema26
    df["sig"]   = df.macd.ewm(span=9).mean()
    m_prev,m_cur = df.macd.iloc[-2:]
    s_prev,s_cur = df.sig .iloc[-2:]
    if m_prev < s_prev and m_cur > s_cur: return "long"
    if m_prev > s_prev and m_cur < s_cur: return "short"
    return "hold"

@app.get("/")
def root(): return {"status": "ok"}

@app.get("/signal")
def signal(ticker: str = Query("AAPL"), interval: str = Query("1h")):
    df = yf.download(ticker, period="14d", interval=interval)[["Close"]].dropna()
    if len(df) < 30:
        return {"error": "not-enough-data"}
    action = macd(df)
    trade = {
        "ts": int(time.time()),
        "ticker": ticker,
        "price": float(df.Close.iloc[-1]),
        "signal": action
    }
    save_trade(trade)
    return trade

@app.get("/trades")
def trades():
    with open(LOG) as f:
        return json.load(f)
