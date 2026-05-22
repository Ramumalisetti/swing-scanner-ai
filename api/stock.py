"""
Vercel Serverless Function — /api/stock?sym=RELIANCE
Returns single stock detailed scan result
"""
import json
from urllib.parse import parse_qs, urlparse
try:
    import numpy as np
    import yfinance as yf
except Exception:
    np = None
    yf = None

# Re-use the same score engine (imported inline for serverless isolation)
# The full indicator code is duplicated here for serverless independence

def _ema(s,p):
    r=np.full(len(s),np.nan)
    if len(s)<p: return r
    k=2.0/(p+1); r[p-1]=s[:p].mean()
    for i in range(p,len(s)): r[i]=s[i]*k+r[i-1]*(1-k)
    return r
def _sma(s,p):
    r=np.full(len(s),np.nan)
    for i in range(p-1,len(s)): r[i]=s[i-p+1:i+1].mean()
    return r
def _rsi(s,p=14):
    r=np.full(len(s),np.nan)
    if len(s)<p+1: return r
    d=np.diff(s); g=np.where(d>0,d,0.0); l=np.where(d<0,-d,0.0)
    ag=g[:p].mean(); al=l[:p].mean()
    for i in range(p,len(s)):
        idx=i-p; ag=(ag*(p-1)+g[idx])/p; al=(al*(p-1)+l[idx])/p
        r[i]=100.0 if al==0 else 100-100/(1+ag/al)
    return r
def _macd(s,f=12,sl=26,sg=9):
    ml=_ema(s,f)-_ema(s,sl); sig=_ema(ml,sg); return ml,sig,ml-sig
def _atr(h,l,c,p=14):
    n=len(c); tr=np.zeros(n)
    for i in range(1,n): tr[i]=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
    r=np.full(n,np.nan)
    if n>=p:
        r[p-1]=tr[1:p].mean()
        for i in range(p,n): r[i]=(r[i-1]*(p-1)+tr[i])/p
    return r


SYMBOL_MAP = {
    "RELIANCE":"RELIANCE.NS","HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS",
    "TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","BHARTIARTL":"BHARTIARTL.NS",
    "HCLTECH":"HCLTECH.NS","BAJFINANCE":"BAJFINANCE.NS","LT":"LT.NS",
    "AXISBANK":"AXISBANK.NS","KOTAKBANK":"KOTAKBANK.NS","MARUTI":"MARUTI.NS",
    "WIPRO":"WIPRO.NS","M&M":"M&M.NS","NTPC":"NTPC.NS","POWERGRID":"POWERGRID.NS",
    "SUNPHARMA":"SUNPHARMA.NS","TITAN":"TITAN.NS","TATAMOTORS":"TATAMOTORS.NS",
    "ZOMATO":"ZOMATO.NS","BEL":"BEL.NS","HAL":"HAL.NS","TRENT":"TRENT.NS",
    "PERSISTENT":"PERSISTENT.NS","COFORGE":"COFORGE.NS","TECHM":"TECHM.NS",
    "JSWSTEEL":"JSWSTEEL.NS","TATASTEEL":"TATASTEEL.NS","COALINDIA":"COALINDIA.NS",
}

def handler(request):
    """Vercel Serverless Function for Stock Details"""
    try:
        query_string = request.url.split('?', 1)[1] if '?' in request.url else ""
        params = parse_qs(query_string)
        sym = params.get("sym", ["RELIANCE"])[0].upper()
        yf_sym = SYMBOL_MAP.get(sym, sym + ".NS")

        tk = yf.Ticker(yf_sym)
        df = tk.history(period="252d", interval="1d", auto_adjust=True)
        if df.empty:
            raise ValueError("No data")
        df.columns = [x.lower() for x in df.columns]
        c = df["close"].values.astype(float)
        h = df["high"].values.astype(float)
        l = df["low"].values.astype(float)
        o = df["open"].values.astype(float)
        v = df["volume"].values.astype(float)
        n = len(c)
        e9 = _ema(c, 9)
        e21 = _ema(c, 21)
        r14 = _rsi(c, 14)
        ml, sl, mh = _macd(c)
        atr = _atr(h, l, c, 14)
        avg_vol = v[-20:].mean() if n >= 20 else v.mean()
        h52 = h[-252:].max() if n >= 252 else h.max()
        atr_v = float(atr[-1]) if not np.isnan(atr[-1]) else c[-1] * 0.01

        result = {
            "sym": sym,
            "spot": round(float(c[-1]), 2),
            "ema9": round(float(e9[-1]), 2),
            "ema21": round(float(e21[-1]), 2),
            "rsi": round(float(r14[-1]), 1),
            "macd": round(float(ml[-1]), 3),
            "macd_sig": round(float(sl[-1]), 3),
            "vol_ratio": round(float(v[-1] / avg_vol), 1),
            "h52": round(float(h52), 2),
            "pct_from_52w": round(
                (float(c[-1]) - float(h52)) / float(h52) * 100, 2
            ),
            "pct_1d": round((float(c[-1]) - float(c[-2])) / float(c[-2]) * 100, 2)
            if n > 1
            else 0,
            "t1": round(float(c[-1]) + atr_v * 2, 2),
            "sl": round(float(c[-1]) - atr_v * 1.5, 2),
            "atr": round(atr_v, 2),
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"ok": True, "data": result}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": False, "error": str(e)}),
        }


# Export handler for Vercel
app = handler
