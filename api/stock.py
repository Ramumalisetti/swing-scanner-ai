"""
Vercel Serverless Function — /api/stock
Stock details endpoint
"""

from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

try:
    import numpy as np
    import yfinance as yf
except Exception as e:
    IMPORT_ERROR = str(e)

SYMBOL_MAP = {
    "RELIANCE":"RELIANCE.NS", "HDFCBANK":"HDFCBANK.NS", "ICICIBANK":"ICICIBANK.NS",
    "INFY":"INFY.NS", "TCS":"TCS.NS",
}

@app.route('/')
def get_stock():
    try:
        sym = request.args.get('sym', 'RELIANCE').upper()
        yf_sym = SYMBOL_MAP.get(sym, sym + ".NS")
        
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period="60d", interval="1d", auto_adjust=True)
        
        if df.empty:
            return jsonify({"ok": False, "error": "No data"}), 400
        
        c = df["Close"].values.astype(float)
        price = round(float(c[-1]), 2)
        
        return jsonify({
            "ok": True,
            "sym": sym,
            "price": price,
            "pct_change": round((c[-1] - c[-2]) / c[-2] * 100, 2) if len(c) > 1 else 0,
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }), 500

if __name__ == '__main__':
    app.run()
