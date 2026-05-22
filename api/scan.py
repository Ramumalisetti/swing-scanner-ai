"""
Vercel Serverless Function — /api/scan
Swing Scanner: 10-Factor Engine · Live Yahoo Finance
"""

from flask import Flask, request, jsonify
import json
from urllib.parse import parse_qs
import traceback

app = Flask(__name__)

try:
    import numpy as np
    import pandas as pd
    import yfinance as yf
except Exception as e:
    IMPORT_ERROR = str(e)
    DEPS_AVAILABLE = False

# Stock list
FNO_STOCKS = [
    {"sym":"RELIANCE",   "yf":"RELIANCE.NS",   "sector":"Energy",   "mcap":"Large"},
    {"sym":"HDFCBANK",   "yf":"HDFCBANK.NS",   "sector":"Banking",  "mcap":"Large"},
    {"sym":"ICICIBANK",  "yf":"ICICIBANK.NS",  "sector":"Banking",  "mcap":"Large"},
    {"sym":"INFY",       "yf":"INFY.NS",       "sector":"IT",       "mcap":"Large"},
    {"sym":"TCS",        "yf":"TCS.NS",        "sector":"IT",       "mcap":"Large"},
]

@app.route('/')
def scan():
    try:
        sector = request.args.get('sector', 'ALL')
        top_n = int(request.args.get('top', 30))
        
        stocks = FNO_STOCKS.copy()
        if sector != "ALL":
            stocks = [s for s in stocks if s["sector"] == sector]
        stocks = stocks[:top_n]
        
        results = []
        for stk in stocks:
            try:
                ticker = yf.Ticker(stk["yf"])
                df = ticker.history(period="60d", interval="1d", auto_adjust=True)
                if df.empty or len(df) < 10:
                    continue
                
                price = float(df["Close"].iloc[-1])
                results.append({
                    "sym": stk["sym"],
                    "sector": stk["sector"],
                    "price": round(price, 2),
                })
            except Exception as e:
                pass
        
        return jsonify({
            "ok": True,
            "count": len(results),
            "stocks": results[:top_n],
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }), 500

if __name__ == '__main__':
    app.run()
