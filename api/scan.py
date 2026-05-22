"""
Vercel Serverless Function — /api/scan
Swing Scanner: 10-Factor Engine · Live Yahoo Finance
Called by the frontend dashboard via fetch('/api/scan?top=30&sector=ALL')
"""

import json
from urllib.parse import parse_qs, urlparse

try:
    import numpy as np
    import pandas as pd
    import yfinance as yf
    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# ── TOP 50 NSE F&O STOCKS (by index weight — fastest for Vercel) ──────────
FNO_STOCKS = [
    {"sym":"RELIANCE",   "yf":"RELIANCE.NS",   "sector":"Energy",   "mcap":"Large"},
    {"sym":"HDFCBANK",   "yf":"HDFCBANK.NS",   "sector":"Banking",  "mcap":"Large"},
    {"sym":"ICICIBANK",  "yf":"ICICIBANK.NS",  "sector":"Banking",  "mcap":"Large"},
    {"sym":"INFY",       "yf":"INFY.NS",       "sector":"IT",       "mcap":"Large"},
    {"sym":"TCS",        "yf":"TCS.NS",        "sector":"IT",       "mcap":"Large"},
    {"sym":"BHARTIARTL", "yf":"BHARTIARTL.NS", "sector":"Telecom",  "mcap":"Large"},
    {"sym":"SBIN",       "yf":"SBIN.NS",       "sector":"Banking",  "mcap":"Large"},
    {"sym":"HCLTECH",    "yf":"HCLTECH.NS",    "sector":"IT",       "mcap":"Large"},
    {"sym":"BAJFINANCE", "yf":"BAJFINANCE.NS", "sector":"Finance",  "mcap":"Large"},
    {"sym":"LT",         "yf":"LT.NS",         "sector":"Infra",    "mcap":"Large"},
    {"sym":"AXISBANK",   "yf":"AXISBANK.NS",   "sector":"Banking",  "mcap":"Large"},
    {"sym":"KOTAKBANK",  "yf":"KOTAKBANK.NS",  "sector":"Banking",  "mcap":"Large"},
    {"sym":"MARUTI",     "yf":"MARUTI.NS",     "sector":"Auto",     "mcap":"Large"},
    {"sym":"WIPRO",      "yf":"WIPRO.NS",      "sector":"IT",       "mcap":"Large"},
    {"sym":"M&M",        "yf":"M&M.NS",        "sector":"Auto",     "mcap":"Large"},
    {"sym":"NTPC",       "yf":"NTPC.NS",       "sector":"Power",    "mcap":"Large"},
    {"sym":"POWERGRID",  "yf":"POWERGRID.NS",  "sector":"Power",    "mcap":"Large"},
    {"sym":"SUNPHARMA",  "yf":"SUNPHARMA.NS",  "sector":"Pharma",   "mcap":"Large"},
    {"sym":"TITAN",      "yf":"TITAN.NS",      "sector":"Consumer", "mcap":"Large"},
    {"sym":"ULTRACEMCO", "yf":"ULTRACEMCO.NS", "sector":"Cement",   "mcap":"Large"},
    {"sym":"TATAMOTORS", "yf":"TATAMOTORS.NS", "sector":"Auto",     "mcap":"Large"},
    {"sym":"TECHM",      "yf":"TECHM.NS",      "sector":"IT",       "mcap":"Large"},
    {"sym":"HINDUNILVR", "yf":"HINDUNILVR.NS", "sector":"FMCG",     "mcap":"Large"},
    {"sym":"EICHERMOT",  "yf":"EICHERMOT.NS",  "sector":"Auto",     "mcap":"Large"},
    {"sym":"JSWSTEEL",   "yf":"JSWSTEEL.NS",   "sector":"Metal",    "mcap":"Large"},
    {"sym":"TATASTEEL",  "yf":"TATASTEEL.NS",  "sector":"Metal",    "mcap":"Large"},
    {"sym":"BAJAJ-AUTO", "yf":"BAJAJ-AUTO.NS", "sector":"Auto",     "mcap":"Large"},
    {"sym":"DRREDDY",    "yf":"DRREDDY.NS",    "sector":"Pharma",   "mcap":"Mid"},
    {"sym":"CIPLA",      "yf":"CIPLA.NS",      "sector":"Pharma",   "mcap":"Mid"},
    {"sym":"COALINDIA",  "yf":"COALINDIA.NS",  "sector":"Metal",    "mcap":"Large"},
    {"sym":"HINDALCO",   "yf":"HINDALCO.NS",   "sector":"Metal",    "mcap":"Large"},
    {"sym":"GRASIM",     "yf":"GRASIM.NS",     "sector":"Cement",   "mcap":"Large"},
    {"sym":"ADANIENT",   "yf":"ADANIENT.NS",   "sector":"Infra",    "mcap":"Large"},
    {"sym":"ADANIPORTS", "yf":"ADANIPORTS.NS", "sector":"Infra",    "mcap":"Large"},
    {"sym":"BEL",        "yf":"BEL.NS",        "sector":"Defence",  "mcap":"Mid"},
    {"sym":"HAL",        "yf":"HAL.NS",        "sector":"Defence",  "mcap":"Mid"},
    {"sym":"IRCTC",      "yf":"IRCTC.NS",      "sector":"PSU",      "mcap":"Mid"},
    {"sym":"ZOMATO",     "yf":"ZOMATO.NS",     "sector":"Retail",   "mcap":"Large"},
    {"sym":"TRENT",      "yf":"TRENT.NS",      "sector":"Retail",   "mcap":"Large"},
    {"sym":"PERSISTENT", "yf":"PERSISTENT.NS", "sector":"IT",       "mcap":"Mid"},
    {"sym":"COFORGE",    "yf":"COFORGE.NS",    "sector":"IT",       "mcap":"Small"},
    {"sym":"DIVISLAB",   "yf":"DIVISLAB.NS",   "sector":"Pharma",   "mcap":"Mid"},
    {"sym":"LUPIN",      "yf":"LUPIN.NS",      "sector":"Pharma",   "mcap":"Mid"},
    {"sym":"BAJAJFINSV", "yf":"BAJAJFINSV.NS", "sector":"Finance",  "mcap":"Large"},
    {"sym":"ITC",        "yf":"ITC.NS",        "sector":"FMCG",     "mcap":"Large"},
    {"sym":"NESTLEIND",  "yf":"NESTLEIND.NS",  "sector":"FMCG",     "mcap":"Mid"},
    {"sym":"DLF",        "yf":"DLF.NS",        "sector":"Realty",   "mcap":"Mid"},
    {"sym":"ONGC",       "yf":"ONGC.NS",       "sector":"Energy",   "mcap":"Large"},
    {"sym":"SHRIRAMFIN", "yf":"SHRIRAMFIN.NS", "sector":"Finance",  "mcap":"Mid"},
    {"sym":"TATACONSUM", "yf":"TATACONSUM.NS", "sector":"FMCG",     "mcap":"Mid"},
]

SECTOR_GROUPS = {
    "IT": ["TCS","INFY","HCLTECH","WIPRO","TECHM","PERSISTENT","COFORGE"],
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "Pharma": ["SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN"],
    "Auto": ["MARUTI","TATAMOTORS","M&M","EICHERMOT","BAJAJ-AUTO"],
    "Metal": ["JSWSTEEL","TATASTEEL","COALINDIA","HINDALCO"],
}


# ══════════════════════════════════════════════════════════════════════
#  INDICATORS
# ══════════════════════════════════════════════════════════════════════
def _ema(s, p):
    r = np.full(len(s), np.nan)
    if len(s) < p: return r
    k = 2.0/(p+1)
    r[p-1] = s[:p].mean()
    for i in range(p, len(s)):
        r[i] = s[i]*k + r[i-1]*(1-k)
    return r

def _sma(s, p):
    r = np.full(len(s), np.nan)
    for i in range(p-1, len(s)):
        r[i] = s[i-p+1:i+1].mean()
    return r

def _rsi(s, p=14):
    r = np.full(len(s), np.nan)
    if len(s) < p+1: return r
    d = np.diff(s)
    g = np.where(d>0, d, 0.0); l = np.where(d<0, -d, 0.0)
    ag = g[:p].mean(); al = l[:p].mean()
    for i in range(p, len(s)):
        idx = i-p
        ag = (ag*(p-1)+g[idx])/p; al = (al*(p-1)+l[idx])/p
        r[i] = 100.0 if al==0 else 100-100/(1+ag/al)
    return r

def _macd(s, fast=12, slow=26, sig=9):
    ml = _ema(s,fast) - _ema(s,slow)
    sl = _ema(ml, sig)
    return ml, sl, ml-sl

def _atr(h, l, c, p=14):
    n = len(c); tr = np.zeros(n)
    for i in range(1,n):
        tr[i] = max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
    r = np.full(n, np.nan)
    if n>=p:
        r[p-1] = tr[1:p].mean()
        for i in range(p,n):
            r[i] = (r[i-1]*(p-1)+tr[i])/p
    return r

def _adx(h, l, c, p=14):
    n = len(c)
    atr_arr = _atr(h, l, c, p)
    pdm = np.zeros(n); ndm = np.zeros(n)
    for i in range(1,n):
        up = h[i]-h[i-1]; dn = l[i-1]-l[i]
        pdm[i] = up if up>dn and up>0 else 0
        ndm[i] = dn if dn>up and dn>0 else 0
    pdi = np.full(n, np.nan); ndi = np.full(n, np.nan); adx = np.full(n, np.nan)
    if n >= p+1:
        st = atr_arr[1:p+1].sum(); sp = pdm[1:p+1].sum(); sn = ndm[1:p+1].sum()
        pdi[p] = 100*sp/st if st>0 else 0
        ndi[p] = 100*sn/st if st>0 else 0
        for i in range(p+1, n):
            st = st-st/p+atr_arr[i]; sp = sp-sp/p+pdm[i]; sn = sn-sn/p+ndm[i]
            pdi[i] = 100*sp/st if st>0 else 0
            ndi[i] = 100*sn/st if st>0 else 0
        dx = np.where((pdi+ndi)>0, 100*np.abs(pdi-ndi)/(pdi+ndi), 0)
        for i in range(2*p, n):
            adx[i] = np.nanmean(dx[p:i+1]) if np.isnan(adx[i-1]) else (adx[i-1]*(p-1)+dx[i])/p
    return adx


# ══════════════════════════════════════════════════════════════════════
#  SCORE ENGINE
# ══════════════════════════════════════════════════════════════════════
def score_stock(df, sym):
    if df is None or len(df) < 50:
        return None
    c = df["close"].values.astype(float)
    h = df["high"].values.astype(float)
    l = df["low"].values.astype(float)
    o = df["open"].values.astype(float)
    v = df["volume"].values.astype(float)
    n = len(c)

    e9  = _ema(c,9);  e21 = _ema(c,21); e50 = _ema(c,50) if n>=50 else np.full(n,np.nan)
    e200= _ema(c,200) if n>=200 else np.full(n,np.nan)
    r14 = _rsi(c,14); ml,sl,mh = _macd(c)
    atr = _atr(h,l,c,14); adx = _adx(h,l,c,14)

    c0=c[-1]; c5=c[-5] if n>5 else c[0]; c20=c[-20] if n>20 else c[0]
    h52 = h[-252:].max() if n>=252 else h.max()
    l52 = l[-252:].min() if n>=252 else l.min()

    def v_(arr): return float(arr[-1]) if not np.isnan(arr[-1]) else 0.0
    e9_v=v_(e9); e21_v=v_(e21); e50_v=v_(e50); e200_v=v_(e200) if n>=200 else c[-100:].mean()
    rsi_v=v_(r14); macd_v=v_(ml); msig_v=v_(sl); mh_v=v_(mh)
    mh_p= float(mh[-2]) if n>2 and not np.isnan(mh[-2]) else 0
    adx_v=v_(adx); atr_v=v_(atr) if v_(atr)>0 else c0*0.01
    avg_vol = v[-20:].mean() if n>=20 else v.mean()
    vol_r   = v[-1]/avg_vol if avg_vol>0 else 1.0
    v5avg   = v[-5:].mean()/avg_vol if avg_vol>0 else 1.0

    score=0; factors=[]; hits=0

    # F1: 52W proximity
    p52 = (c0-h52)/h52*100
    if p52>=0:      score+=25;hits+=1;factors.append({"n":"52W Breakout","p":25,"c":"#00e5a0"})
    elif p52>=-3:   score+=20;hits+=1;factors.append({"n":"Near 52W High","p":20,"c":"#00e5a0"})
    elif p52>=-8:   score+=10;factors.append({"n":"Upper Range","p":10,"c":"#f5c842"})
    else:           factors.append({"n":"52W Far","p":0,"c":"#304560"})

    # F2: EMA alignment
    if e9_v>e21_v and e21_v>e50_v: score+=20;hits+=1;factors.append({"n":"EMA9>21>50 ✅","p":20,"c":"#00e5a0"})
    elif e9_v>e21_v:                score+=12;factors.append({"n":"EMA9>21","p":12,"c":"#f5c842"})
    else:                           factors.append({"n":"EMA Bearish","p":0,"c":"#304560"})

    # F3: RSI zone
    if 55<=rsi_v<=65:   score+=15;hits+=1;factors.append({"n":"RSI Sweet 55-65 ✅","p":15,"c":"#00e5a0"})
    elif 50<=rsi_v<=70: score+=10;factors.append({"n":"RSI Bullish","p":10,"c":"#f5c842"})
    elif 45<=rsi_v<50:  score+=5;factors.append({"n":"RSI Near 50","p":5,"c":"#f5c842"})
    else:               factors.append({"n":"RSI Weak","p":0,"c":"#304560"})

    # F4: Volume
    if vol_r>=3:   score+=20;hits+=1;factors.append({"n":"Vol 3x+ Surge ✅","p":20,"c":"#00e5a0"})
    elif vol_r>=2: score+=18;hits+=1;factors.append({"n":"Vol 2x Breakout ✅","p":18,"c":"#00e5a0"})
    elif vol_r>=1.5: score+=12;factors.append({"n":"Above Avg Vol","p":12,"c":"#f5c842"})
    elif v5avg>=1.5: score+=8;factors.append({"n":"5D Vol Rising","p":8,"c":"#f5c842"})
    else:          factors.append({"n":"Low Volume","p":0,"c":"#304560"})

    # F5: MACD
    if mh_v>0 and mh_p<=0:     score+=15;hits+=1;factors.append({"n":"MACD Fresh Cross ✅","p":15,"c":"#00e5a0"})
    elif mh_v>0 and mh_v>mh_p: score+=10;factors.append({"n":"MACD Rising","p":10,"c":"#f5c842"})
    elif mh_v>0:                score+=6;factors.append({"n":"MACD Bullish","p":6,"c":"#f5c842"})
    else:                       factors.append({"n":"MACD Bear","p":0,"c":"#304560"})

    # F6: Consolidation breakout
    lb = min(15, n-5)
    rh = h[-lb-1:-1].max(); rl = l[-lb-1:-1].min()
    rng_pct = (rh-rl)/rl*100
    if rng_pct<8 and c0>rh: score+=20;hits+=1;factors.append({"n":"Squeeze Breakout ✅","p":20,"c":"#00e5a0"})
    elif c0>rh:              score+=12;factors.append({"n":"Range Breakout","p":12,"c":"#f5c842"})
    elif rng_pct<8:          score+=8;factors.append({"n":"Tight Consolidation","p":8,"c":"#f5c842"})
    else:                    factors.append({"n":"Inside Range","p":0,"c":"#304560"})

    # F7: ADX
    if adx_v>=30: score+=15;hits+=1;factors.append({"n":"ADX Strong 30+ ✅","p":15,"c":"#00e5a0"})
    elif adx_v>=25: score+=10;factors.append({"n":"ADX Trending","p":10,"c":"#f5c842"})
    elif adx_v>=20: score+=5;factors.append({"n":"ADX Building","p":5,"c":"#f5c842"})
    else:           factors.append({"n":"ADX Weak","p":0,"c":"#304560"})

    # F8: Above 200 EMA
    if c0>e200_v: score+=10;hits+=1;factors.append({"n":"Above 200 EMA ✅","p":10,"c":"#00e5a0"})
    else:         factors.append({"n":"Below 200 EMA","p":0,"c":"#304560"})

    # F9: Candle
    body = abs(c[-1]-o[-1]); is_bull = c[-1]>o[-1]
    is_big = body>atr_v*0.6
    is_eng = is_bull and n>2 and c[-1]>o[-2] and o[-1]<c[-2]
    if is_eng and is_big: score+=10;hits+=1;factors.append({"n":"Bullish Engulf ✅","p":10,"c":"#00e5a0"})
    elif is_bull and is_big: score+=7;factors.append({"n":"Strong Bull Bar","p":7,"c":"#f5c842"})
    elif is_bull:            score+=4;factors.append({"n":"Bull Close","p":4,"c":"#f5c842"})
    else:                    factors.append({"n":"Bear Bar","p":0,"c":"#304560"})

    # F10: 5D Momentum
    m5 = (c0-c5)/c5*100
    if m5>=3:    score+=10;hits+=1;factors.append({"n":"5D Momentum ✅","p":10,"c":"#00e5a0"})
    elif m5>=1.5: score+=7;factors.append({"n":"Rising 5D","p":7,"c":"#f5c842"})
    elif m5>=0:  score+=3;factors.append({"n":"Flat 5D","p":3,"c":"#f5c842"})
    else:        factors.append({"n":"Falling 5D","p":0,"c":"#304560"})

    # Grade
    if score>=100:  grade="A+ FIRE 🔥"; conf="~72-78%"
    elif score>=80: grade="A STRONG ✅"; conf="~65-72%"
    elif score>=65: grade="B GOOD 📈";   conf="~55-65%"
    elif score>=50: grade="C WATCH 👀";  conf="~42-55%"
    else:           grade="F SKIP ❌";   conf="<30%"

    t1 = round(c0+atr_v*2.0, 2); t2 = round(c0+atr_v*3.5, 2)
    sl = round(c0-atr_v*1.5, 2)
    r52 = h52-l52
    pos52 = round((c0-l52)/r52*100,1) if r52>0 else 50

    return {
        "sym":sym, "score":score, "grade":grade, "conf":conf,
        "hits":hits,
        "factors":[{"n":f["n"],"p":f["p"],"c":f["c"]} for f in factors if f["p"]>0],
        "spot":round(c0,2), "pct1d":round((c0-c[-2])/c[-2]*100,2) if n>1 else 0,
        "pct5d":round(m5,2), "rsi":round(rsi_v,1),
        "adx":round(adx_v,1), "vol":round(vol_r,1),
        "ema9":round(e9_v,2), "ema21":round(e21_v,2), "ema50":round(e50_v,2),
        "h52":round(h52,2), "pct52":round(p52,2), "pos52":pos52,
        "t1":t1, "t2":t2, "sl":sl,
        "t1pct":round((t1-c0)/c0*100,2), "t2pct":round((t2-c0)/c0*100,2),
        "slpct":round((c0-sl)/c0*100,2),
        "rr":round(((t1-c0)/(c0-sl)),2) if c0>sl else 0,
        "atr":round(atr_v,2),
    }


def fetch_stock(yf_sym, days=252):
    ticker = yf.Ticker(yf_sym)
    df = ticker.history(period=f"{days}d", interval="1d", auto_adjust=True)
    if df.empty or len(df) < 30:
        return None
    df = df[["Open","High","Low","Close","Volume"]].copy()
    df.columns = ["open","high","low","close","volume"]
    return df.dropna().reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════
#  VERCEL SERVERLESS HANDLER
# ══════════════════════════════════════════════════════════════════════
def handler(request):
    """Vercel Serverless Function for Swing Scanner"""
    try:
        if not DEPS_AVAILABLE:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"ok": False, "error": f"Import error: {IMPORT_ERROR}"}),
            }
        
        # Parse query parameters from request
        query_string = ""
        if hasattr(request, 'url'):
            query_string = request.url.split('?', 1)[1] if '?' in request.url else ""
        elif hasattr(request, 'query_string'):
            query_string = request.query_string.decode() if isinstance(request.query_string, bytes) else request.query_string
        elif isinstance(request, dict) and 'querystring' in request:
            query_string = request['querystring']
        params = parse_qs(query_string)
        sector = params.get("sector", ["ALL"])[0]
        top_n = int(params.get("top", [30])[0])
        min_sc = int(params.get("min", [50])[0])

        # Filter stock list
        stocks = FNO_STOCKS.copy()
        if sector != "ALL":
            stocks = [s for s in stocks if s["sector"] == sector]
        stocks = stocks[:top_n]

        results = []
        errors = []

        for stk in stocks:
            try:
                df = fetch_stock(stk["yf"], days=252)
                r = score_stock(df, stk["sym"])
                if r:
                    r["sector"] = stk["sector"]
                    r["mcap"] = stk["mcap"]
                    results.append(r)
            except Exception as e:
                errors.append({"sym": stk["sym"], "error": str(e)})

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Filter by min score
        top_results = [r for r in results if r["score"] >= min_sc]

        from datetime import datetime
        payload = {
            "ok": True,
            "scanned": len(results),
            "fire": len([r for r in results if r["score"] >= 100]),
            "strong": len([r for r in results if 80 <= r["score"] < 100]),
            "watch": len([r for r in results if 50 <= r["score"] < 80]),
            "errors": len(errors),
            "stocks": results,
            "scan_time": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(payload),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": False, "error": str(e)}),
        }


# Export handler for Vercel
app = handler
