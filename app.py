"""
ATLAS v4.0 — Quantitative Trading Intelligence
Bulletproof universal data fetching with retry logic + 8 strategies
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings, os, time, json
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATLAS — Trading Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=Bebas+Neue&display=swap');
:root{
  --bg:#08090d;--bg2:#0e1118;--card:#111520;--border:rgba(255,255,255,0.06);
  --gold:#c9a84c;--teal:#00d4aa;--red:#ff4d6d;--blue:#4d9fff;--purple:#a78bfa;
  --t1:#eef0f4;--t2:#8892a4;--t3:#4a5568;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--t1);}
.stApp{background:var(--bg);}
#MainMenu,footer,.stDeployButton,header{display:none!important;}
.block-container{padding:0 2rem 4rem!important;max-width:1440px!important;}

/* Header */
.hdr{background:var(--bg2);border-bottom:1px solid var(--border);
  padding:1.4rem 0 1.2rem;margin:0 -2rem 2rem;text-align:center;position:relative;}
.hdr::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:600px;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);}
.logo{font-family:'Bebas Neue',sans-serif;font-size:3.2rem;letter-spacing:.18em;line-height:1;}
.logo span{color:var(--gold);}
.sub{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.25em;color:var(--t3);text-transform:uppercase;}

/* Inputs */
.stTextInput>div>div>input{
  background:#060810!important;border:1px solid rgba(201,168,76,.3)!important;
  border-radius:3px!important;color:var(--t1)!important;
  font-family:'Space Mono',monospace!important;font-size:1rem!important;padding:.8rem 1.1rem!important;}
.stTextInput>div>div>input:focus{border-color:var(--gold)!important;box-shadow:0 0 0 1px rgba(201,168,76,.25)!important;}
.stButton>button{
  background:linear-gradient(135deg,#c9a84c,#a07830)!important;border:none!important;
  border-radius:3px!important;color:#08090d!important;font-family:'Bebas Neue',sans-serif!important;
  font-size:1.15rem!important;letter-spacing:.1em!important;padding:.72rem 1.8rem!important;
  width:100%!important;}
.stButton>button:hover{opacity:.85!important;}
.stSelectbox>div>div{background:#060810!important;border-color:rgba(201,168,76,.2)!important;
  color:var(--t1)!important;font-family:'Space Mono',monospace!important;}

/* Cards */
.card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:1.4rem;margin-bottom:1rem;}
.ca-teal{border-left:2px solid var(--teal);}
.ca-gold{border-left:2px solid var(--gold);}
.ca-purple{border-left:2px solid var(--purple);}
.ct{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.2em;text-transform:uppercase;color:var(--t3);margin-bottom:.9rem;}

/* Metrics */
.mg{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.75rem;margin-bottom:1rem;}
.mt{background:#0b0e17;border:1px solid var(--border);border-radius:3px;padding:.9rem 1rem;}
.ml{font-family:'Space Mono',monospace;font-size:.5rem;letter-spacing:.18em;color:var(--t3);text-transform:uppercase;margin-bottom:.28rem;}
.mv{font-family:'Space Mono',monospace;font-size:1.1rem;font-weight:700;color:var(--t1);}
.mc{font-size:.7rem;margin-top:.15rem;}
.up{color:var(--teal);}.dn{color:var(--red);}

/* Strategy rows */
.sr{display:flex;align-items:center;justify-content:space-between;padding:.75rem 0;border-bottom:1px solid var(--border);}
.sr:last-child{border-bottom:none;}
.sn{font-family:'DM Sans',sans-serif;font-size:.86rem;font-weight:500;color:var(--t2);flex:1;}
.sd{font-family:'Space Mono',monospace;font-size:.6rem;color:var(--t3);flex:2;padding:0 .75rem;}
.vb{font-family:'Space Mono',monospace;font-size:.68rem;font-weight:700;padding:.26rem .8rem;border-radius:2px;min-width:62px;text-align:center;}
.vbuy{background:rgba(0,212,170,.15);color:var(--teal);border:1px solid rgba(0,212,170,.35);}
.vsell{background:rgba(255,77,109,.15);color:var(--red);border:1px solid rgba(255,77,109,.35);}
.vhold{background:rgba(77,159,255,.1);color:var(--blue);border:1px solid rgba(77,159,255,.25);}

/* Tally */
.tb{display:flex;gap:.5rem;margin:1rem 0;}
.ti{flex:1;padding:.85rem;border-radius:3px;text-align:center;}
.tn{font-size:1.9rem;font-weight:700;line-height:1;font-family:'Space Mono',monospace;}
.tl{font-size:.56rem;letter-spacing:.15em;margin-top:.22rem;color:rgba(255,255,255,.4);font-family:'Space Mono',monospace;}
.tbuy{background:rgba(0,212,170,.1);border:1px solid rgba(0,212,170,.25);}
.tsell{background:rgba(255,77,109,.1);border:1px solid rgba(255,77,109,.25);}
.thold{background:rgba(77,159,255,.07);border:1px solid rgba(77,159,255,.2);}
.tn.buy{color:var(--teal);}.tn.sell{color:var(--red);}.tn.hold{color:var(--blue);}

/* Recommendation */
.rb{border-radius:4px;padding:1.8rem 2rem;border-width:1px;border-style:solid;}
.rbuy{background:rgba(0,212,170,.05);border-color:rgba(0,212,170,.3);}
.rsell{background:rgba(255,77,109,.05);border-color:rgba(255,77,109,.3);}
.rhold{background:rgba(77,159,255,.04);border-color:rgba(77,159,255,.25);}
.rv{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:.08em;line-height:1;}
.rtk{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.2em;color:var(--t3);margin-bottom:1rem;}
.rbody{font-family:'DM Sans',sans-serif;font-size:.88rem;line-height:1.75;color:var(--t2);}
.rbody strong{color:var(--t1);font-weight:600;}
.rbody p{margin-bottom:.85rem;}

/* News */
.ni{display:flex;align-items:flex-start;gap:.8rem;padding:.75rem 0;border-bottom:1px solid var(--border);}
.ni:last-child{border-bottom:none;}
.nd{width:7px;height:7px;border-radius:50%;margin-top:.38rem;flex-shrink:0;}
.npos{background:var(--teal);}.nneg{background:var(--red);}.nneut{background:var(--t3);}
.nh{font-size:.84rem;color:var(--t2);line-height:1.42;flex:1;}
.ns{font-family:'Space Mono',monospace;font-size:.54rem;padding:.16rem .45rem;border-radius:2px;flex-shrink:0;margin-top:.12rem;}
.spos{background:rgba(0,212,170,.12);color:var(--teal);}
.sneg{background:rgba(255,77,109,.12);color:var(--red);}
.sneut{background:rgba(74,85,104,.3);color:var(--t3);}

/* Divider */
.sdiv{display:flex;align-items:center;gap:1rem;margin:1.8rem 0 1.2rem;}
.sl_{flex:1;height:1px;background:var(--border);}
.slbl{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.2em;color:var(--t3);text-transform:uppercase;white-space:nowrap;}

/* Level tags */
.lr{display:flex;gap:.38rem;flex-wrap:wrap;margin:.3rem 0;}
.lt{font-family:'Space Mono',monospace;font-size:.6rem;padding:.2rem .5rem;border-radius:2px;}
.lts{background:rgba(0,212,170,.08);border:1px solid rgba(0,212,170,.3);color:var(--teal);}
.ltr{background:rgba(255,77,109,.08);border:1px solid rgba(255,77,109,.3);color:var(--red);}

/* Win prob */
.wpn{font-family:'Bebas Neue',sans-serif;font-size:4.2rem;letter-spacing:.05em;line-height:1;}
.wpl{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.2em;color:var(--t3);margin-top:.28rem;}

/* Status box */
.status-ok{background:rgba(0,212,170,.06);border:1px solid rgba(0,212,170,.25);border-radius:3px;
  padding:.6rem 1rem;font-family:'Space Mono',monospace;font-size:.7rem;color:var(--teal);margin-bottom:.8rem;}
.status-warn{background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.25);border-radius:3px;
  padding:.6rem 1rem;font-family:'Space Mono',monospace;font-size:.7rem;color:var(--gold);margin-bottom:.8rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hdr">
  <div class="logo">AT<span>L</span>AS</div>
  <div class="sub">Quantitative Trading Intelligence · v4.0 · Universal · 8 Strategies</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────
def fmt(n, pre="", suf="", dec=2):
    if n is None: return "N/A"
    try:
        n = float(n)
        if np.isnan(n): return "N/A"
        if abs(n) >= 1e12: return f"{pre}{n/1e12:.{dec}f}T{suf}"
        if abs(n) >= 1e9:  return f"{pre}{n/1e9:.{dec}f}B{suf}"
        if abs(n) >= 1e6:  return f"{pre}{n/1e6:.{dec}f}M{suf}"
        return f"{pre}{n:,.{dec}f}{suf}"
    except: return "N/A"

def pct(n):
    try:
        v = float(n)
        return "N/A" if np.isnan(v) else f"{v*100:+.2f}%"
    except: return "N/A"

def ps(p):
    """Format price with appropriate decimal places"""
    try:
        p = float(p)
        if p < 0.0001: return f"${p:.8f}"
        if p < 0.01:   return f"${p:.6f}"
        if p < 1:      return f"${p:.4f}"
        if p < 10:     return f"${p:.3f}"
        return f"${p:,.2f}"
    except: return "N/A"

def sg(obj, key, default=None):
    try:
        v = obj.get(key, default)
        if v is None: return default
        if isinstance(v, float) and np.isnan(v): return default
        return v
    except: return default

def divider(label):
    st.markdown(f'<div class="sdiv"><div class="sl_"></div>'
                f'<div class="slbl">◈ {label}</div>'
                f'<div class="sl_"></div></div>', unsafe_allow_html=True)

def badge(vote):
    cls = {"BUY": "vbuy", "SELL": "vsell", "HOLD": "vhold"}.get(vote, "vhold")
    return f'<span class="vb {cls}">{vote}</span>'

def mtile(label, val, sub="", sc=""):
    sh = f'<div class="mc {sc}">{sub}</div>' if sub else ""
    return f'<div class="mt"><div class="ml">{label}</div><div class="mv">{val}</div>{sh}</div>'

# ─────────────────────────────────────────────────────────────
# KNOWN CRYPTO SYMBOLS
# ─────────────────────────────────────────────────────────────
CRYPTO_SYMBOLS = {
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","AVAX","DOT","MATIC","LTC","LINK",
    "UNI","ATOM","XLM","ALGO","FIL","NEAR","APT","ARB","OP","SHIB","PEPE","TRX",
    "TON","SUI","SEI","INJ","FET","RNDR","GRT","AAVE","CRV","MKR","COMP","FTM",
    "SAND","MANA","AXS","BAT","NEO","EOS","ICP","HBAR","XTZ","THETA","VET",
    "FLOKI","BONK","WIF","TRUMP","EGLD","SNX","YFI","1INCH","ENJ","GALA","POPCAT",
    "BRETT","WBTC","USDT","USDC","BUSD","DAI","STETH","BABYDOGE","BCH","ETC",
}

COIN_ID_MAP = {
    "BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","SOL":"solana",
    "XRP":"ripple","ADA":"cardano","DOGE":"dogecoin","AVAX":"avalanche-2",
    "DOT":"polkadot","MATIC":"matic-network","LTC":"litecoin","LINK":"chainlink",
    "UNI":"uniswap","ATOM":"cosmos","XLM":"stellar","ALGO":"algorand",
    "FIL":"filecoin","NEAR":"near","APT":"aptos","ARB":"arbitrum","OP":"optimism",
    "SHIB":"shiba-inu","PEPE":"pepe","TRX":"tron","TON":"the-open-network",
    "SUI":"sui","SEI":"sei-network","INJ":"injective-protocol","FET":"fetch-ai",
    "RNDR":"render-token","GRT":"the-graph","AAVE":"aave","CRV":"curve-dao-token",
    "MKR":"maker","COMP":"compound-governance-token","FTM":"fantom",
    "SAND":"the-sandbox","MANA":"decentraland","AXS":"axie-infinity",
    "BAT":"basic-attention-token","NEO":"neo","EOS":"eos","ICP":"internet-computer",
    "HBAR":"hedera-hashgraph","XTZ":"tezos","THETA":"theta-token","VET":"vechain",
    "FLOKI":"floki","BONK":"bonk","WIF":"dogwifcoin","TRUMP":"maga",
    "EGLD":"elrond-erd-2","SNX":"havven","YFI":"yearn-finance","1INCH":"1inch",
    "ENJ":"enjincoin","GALA":"gala","POPCAT":"popcat","BRETT":"brett",
    "WBTC":"wrapped-bitcoin","BCH":"bitcoin-cash","ETC":"ethereum-classic",
    "BABYDOGE":"baby-doge-coin",
}

# ─────────────────────────────────────────────────────────────
# ROBUST HTTP REQUEST
# ─────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def robust_get(url, retries=3, delay=2, timeout=15, params=None):
    """GET with retry + exponential backoff. Returns (response_json, error_str)"""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, params=params)
            if r.status_code == 200:
                return r.json(), None
            if r.status_code == 429:
                # Rate limited — wait longer
                wait = delay * (2 ** attempt) + 2
                time.sleep(wait)
                continue
            if r.status_code == 404:
                return None, f"404: Not found at {url}"
            return None, f"HTTP {r.status_code}"
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return None, "Request timed out"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            return None, str(e)
    return None, "Max retries exceeded"

# ─────────────────────────────────────────────────────────────
# SEARCH (suggestions)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=7200, show_spinner=False)
def search_markets(query: str):
    """Search both Yahoo Finance and CoinGecko for ticker suggestions"""
    results = []
    seen = set()

    # Yahoo Finance search
    try:
        data, err = robust_get(
            f"https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": query, "quotesCount": 8, "newsCount": 0},
            retries=2, delay=1
        )
        if data:
            for q in data.get("quotes", []):
                sym = q.get("symbol", "")
                name = q.get("longname") or q.get("shortname") or ""
                exch = q.get("exchDisp", "")
                qt = q.get("quoteType", "")
                if sym and name and sym not in seen:
                    results.append({
                        "sym": sym, "name": name[:50],
                        "exch": exch, "type": qt, "source": "stock"
                    })
                    seen.add(sym)
    except Exception:
        pass

    # CoinGecko search
    try:
        data2, err2 = robust_get(
            f"https://api.coingecko.com/api/v3/search?query={query}",
            retries=2, delay=1
        )
        if data2:
            for c in data2.get("coins", [])[:6]:
                sym = c.get("symbol", "").upper()
                name = c.get("name", "")
                cid = c.get("id", "")
                if sym and name and sym not in seen:
                    results.append({
                        "sym": sym, "name": name[:50],
                        "exch": "CRYPTO", "type": "CRYPTOCURRENCY",
                        "source": "crypto", "coin_id": cid
                    })
                    seen.add(sym)
    except Exception:
        pass

    return results[:10]

# ─────────────────────────────────────────────────────────────
# ASSET TYPE DETECTION
# ─────────────────────────────────────────────────────────────
def detect_type(ticker: str) -> str:
    t = ticker.upper().strip()
    # Remove exchange suffix for check
    base = t.split("-")[0].split(".")[0].split("/")[0]
    if base in CRYPTO_SYMBOLS:
        return "crypto"
    # Ask Yahoo Finance
    try:
        info = yf.Ticker(t).fast_info
        # fast_info has quote_type in newer yfinance
        qt = getattr(info, "quote_type", None) or ""
        if qt.upper() == "CRYPTOCURRENCY":
            return "crypto"
    except Exception:
        pass
    try:
        info = yf.Ticker(t).info
        qt = info.get("quoteType", "")
        if qt == "CRYPTOCURRENCY":
            return "crypto"
    except Exception:
        pass
    return "stock"

# ─────────────────────────────────────────────────────────────
# RESOLVE COINGECKO ID
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def resolve_coin_id(symbol_or_name: str) -> str:
    q = symbol_or_name.upper().strip()
    # Direct map first
    if q in COIN_ID_MAP:
        return COIN_ID_MAP[q]
    # CoinGecko search
    try:
        data, _ = robust_get(
            f"https://api.coingecko.com/api/v3/search?query={q.lower()}",
            retries=3, delay=2
        )
        if data:
            coins = data.get("coins", [])
            # Exact symbol match
            for c in coins:
                if c.get("symbol", "").upper() == q:
                    return c["id"]
            # Name contains
            for c in coins:
                if q.lower() in c.get("name", "").lower():
                    return c["id"]
            if coins:
                return coins[0]["id"]
    except Exception:
        pass
    return q.lower()  # last resort

# ─────────────────────────────────────────────────────────────
# FETCH STOCK DATA (yfinance — universal)
# ─────────────────────────────────────────────────────────────
def fetch_stock_data(ticker: str):
    """
    Fetch stock OHLCV via yfinance.
    Tries multiple periods and clears stale cache automatically.
    Returns (df, info, error_msg)
    """
    df = None
    info = {}
    last_err = ""

    for period in ["6mo", "3mo", "1mo"]:
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(period=period, interval="1d", auto_adjust=True, actions=False)

            if df is not None and not df.empty:
                # Normalise columns
                df.columns = [str(c).strip() for c in df.columns]
                needed = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
                if "Close" not in needed:
                    last_err = f"No Close column in {period} data"
                    continue
                df = df[needed].copy()
                df.dropna(subset=["Close"], inplace=True)
                df = df[df["Close"] > 0]  # Remove bad rows

                if len(df) >= 15:
                    # Add Volume if missing
                    if "Volume" not in df.columns:
                        df["Volume"] = 0.0
                    if "High" not in df.columns:
                        df["High"] = df["Close"]
                    if "Low" not in df.columns:
                        df["Low"] = df["Close"]
                    if "Open" not in df.columns:
                        df["Open"] = df["Close"]
                    # Get info
                    try:
                        info = tk.info or {}
                    except Exception:
                        info = {}
                    return df, info, None
            last_err = f"Empty data for period={period}"
        except Exception as e:
            last_err = str(e)
            time.sleep(0.5)

    return None, {}, last_err

# ─────────────────────────────────────────────────────────────
# FETCH CRYPTO DATA (CoinGecko — universal)
# ─────────────────────────────────────────────────────────────
def fetch_crypto_data(coin_id: str):
    """
    Fetch crypto OHLCV via CoinGecko with multiple fallbacks.
    Returns (df, error_msg)
    """
    df = None

    # Method 1: OHLC endpoint (best for candlestick)
    for days in [180, 90, 30]:
        data, err = robust_get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": str(days)},
            retries=3, delay=3
        )
        if data and isinstance(data, list) and len(data) >= 10:
            df = pd.DataFrame(data, columns=["ts", "Open", "High", "Low", "Close"])
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
            df.set_index("ts", inplace=True)
            df["Volume"] = 0.0
            break
        if err and "429" in str(err):
            time.sleep(5)  # Rate limit

    # Method 2: Market chart (close + volume, always works)
    if df is None or df.empty:
        for days in [90, 60, 30]:
            data2, err2 = robust_get(
                f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": str(days), "interval": "daily"},
                retries=3, delay=3
            )
            if data2:
                prices = data2.get("prices", [])
                volumes = data2.get("total_volumes", [])
                if len(prices) >= 10:
                    pdf = pd.DataFrame(prices, columns=["ts", "Close"])
                    pdf["ts"] = pd.to_datetime(pdf["ts"], unit="ms").dt.normalize()
                    pdf.set_index("ts", inplace=True)
                    pdf["Open"]  = pdf["Close"].shift(1).fillna(pdf["Close"])
                    pdf["High"]  = pdf[["Open", "Close"]].max(axis=1) * 1.003
                    pdf["Low"]   = pdf[["Open", "Close"]].min(axis=1) * 0.997
                    if volumes:
                        vdf = pd.DataFrame(volumes, columns=["ts", "Volume"])
                        vdf["ts"] = pd.to_datetime(vdf["ts"], unit="ms").dt.normalize()
                        vdf.set_index("ts", inplace=True)
                        pdf["Volume"] = vdf["Volume"].reindex(pdf.index).fillna(0)
                    else:
                        pdf["Volume"] = 0.0
                    df = pdf[["Open", "High", "Low", "Close", "Volume"]]
                    break
            if err2 and "429" in str(err2):
                time.sleep(5)

    # Method 3: Try BTC-USD on Yahoo Finance as last resort
    if df is None or df.empty:
        yf_sym = coin_id.upper() + "-USD"
        df_yf, _, _ = fetch_stock_data(yf_sym)
        if df_yf is not None:
            df = df_yf

    if df is None or df.empty:
        return None, f"Could not fetch data for coin_id='{coin_id}'"

    # Add volume from market_chart if ohlc gave zeros
    if "Volume" in df.columns and df["Volume"].sum() == 0:
        data3, _ = robust_get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": "90", "interval": "daily"},
            retries=2, delay=2
        )
        if data3:
            vol_data = data3.get("total_volumes", [])
            if vol_data:
                vdf = pd.DataFrame(vol_data, columns=["ts", "Volume"])
                vdf["ts"] = pd.to_datetime(vdf["ts"], unit="ms").dt.normalize()
                vdf.set_index("ts", inplace=True)
                df.index = df.index.normalize()
                df["Volume"] = vdf["Volume"].reindex(df.index).fillna(0)

    df.dropna(subset=["Close"], inplace=True)
    df = df[df["Close"] > 0]
    return df, None

def fetch_crypto_meta(coin_id: str):
    data, _ = robust_get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}",
        params={"localization": "false", "tickers": "false",
                "community_data": "false", "developer_data": "false"},
        retries=2, delay=2
    )
    return data or {}

# ─────────────────────────────────────────────────────────────
# NEWS
# ─────────────────────────────────────────────────────────────
POS = {"bullish","surge","rally","gain","profit","growth","record","beat","strong",
       "upgrade","buy","rise","soar","exceed","partnership","approve","launch",
       "expansion","dividend","breakthrough","acquire","win","boost","jump","recover"}
NEG = {"bearish","crash","drop","decline","fall","loss","miss","downgrade","sell",
       "plunge","slump","investigation","lawsuit","ban","default","bankruptcy",
       "fraud","warning","cut","layoff","fine","risk","concern","fear","dump",
       "collapse","selloff","correction","volatile","sued","penalty","probe"}

def sent_score(text: str) -> str:
    t = text.lower()
    p = sum(1 for w in POS if w in t)
    n = sum(1 for w in NEG if w in t)
    if p > n: return "positive"
    if n > p: return "negative"
    return "neutral"

def fetch_news(ticker: str, asset_type: str, coin_name: str = "") -> list:
    headlines = []

    # Source 1: Yahoo Finance RSS (most reliable, no rate limit)
    try:
        import xml.etree.ElementTree as ET
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        r = requests.get(url, timeout=10, headers=HEADERS)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:8]:
                t = item.findtext("title")
                if t and t not in headlines:
                    headlines.append(t)
    except Exception:
        pass

    # Source 2: CryptoCompare for crypto
    if asset_type == "crypto" and len(headlines) < 5:
        try:
            q = coin_name or ticker
            data, _ = robust_get(
                f"https://min-api.cryptocompare.com/data/v2/news/",
                params={"categories": ticker, "excludeCategories": "Sponsored", "lang": "EN"},
                retries=2, delay=1
            )
            if data:
                for art in data.get("Data", [])[:7]:
                    t = art.get("title", "")
                    if t and t not in headlines:
                        headlines.append(t)
        except Exception:
            pass

    # Source 3: CoinGecko news
    if asset_type == "crypto" and len(headlines) < 4:
        try:
            data2, _ = robust_get("https://api.coingecko.com/api/v3/news", retries=1, delay=1)
            if data2:
                for art in data2.get("data", [])[:5]:
                    t = art.get("title", "")
                    if t and t not in headlines:
                        headlines.append(t)
        except Exception:
            pass

    # Source 4: Finnhub (optional env key)
    fkey = os.environ.get("FINNHUB_API_KEY", "")
    if fkey and len(headlines) < 5:
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            data3, _ = robust_get(
                f"https://finnhub.io/api/v1/company-news",
                params={"symbol": ticker, "from": week_ago, "to": today, "token": fkey},
                retries=2, delay=1
            )
            if data3:
                for item in data3[:7]:
                    t = item.get("headline", "")
                    if t and t not in headlines:
                        headlines.append(t)
        except Exception:
            pass

    return [h for h in headlines if h][:10]

def agg_sentiment(headlines):
    if not headlines:
        return "neutral", "No recent news retrieved"
    scores = [sent_score(h) for h in headlines]
    p = scores.count("positive")
    n = scores.count("negative")
    if p > n * 1.2:  return "positive", headlines[0]
    if n > p * 1.2:  return "negative", headlines[0]
    return "neutral", headlines[0]

# ─────────────────────────────────────────────────────────────
# TECHNICAL ANALYSIS
# ─────────────────────────────────────────────────────────────
def calc_ema(s, n): return s.ewm(span=n, adjust=False).mean()
def calc_sma(s, n): return s.rolling(n).mean()

def calc_rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0); l = -d.clip(upper=0)
    ag = g.ewm(com=n-1, adjust=False).mean()
    al = l.ewm(com=n-1, adjust=False).mean()
    rs = ag / al.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))

def calc_macd(s, f=12, sl=26, sig=9):
    ml = calc_ema(s, f) - calc_ema(s, sl)
    signal = calc_ema(ml, sig)
    return ml, signal, ml - signal

def calc_stoch(h, l, c, k=14, d=3):
    lo = l.rolling(k).min(); hi = h.rolling(k).max()
    pk = 100 * (c - lo) / (hi - lo + 1e-10)
    return pk, pk.rolling(d).mean()

def calc_atr(h, l, c, n=14):
    tr = pd.concat([(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=n, adjust=False).mean()

def calc_bb(s, n=20, k=2):
    mid = calc_sma(s, n); std = s.rolling(n).std()
    return mid + k*std, mid, mid - k*std

def calc_vwap(df):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    v = df["Volume"].replace(0, np.nan)
    return (tp * v).cumsum() / v.cumsum()

def calc_fib(h, l):
    d = h - l
    return {
        "0.0 (High)": h, "0.236": h - 0.236*d, "0.382": h - 0.382*d,
        "0.500": h - 0.500*d, "0.618": h - 0.618*d,
        "0.786": h - 0.786*d, "1.0 (Low)": l
    }

def calc_pivots(h, l, w=5):
    ph, pl = [], []
    for i in range(w, len(h) - w):
        if h.iloc[i] == h.iloc[i-w:i+w+1].max():
            ph.append((h.index[i], float(h.iloc[i])))
        if l.iloc[i] == l.iloc[i-w:i+w+1].min():
            pl.append((l.index[i], float(l.iloc[i])))
    return ph, pl

def detect_fvg(df):
    fvgs = []
    for i in range(2, len(df)):
        if df["Low"].iloc[i] > df["High"].iloc[i-2]:
            fvgs.append({"t": "bull", "top": df["Low"].iloc[i], "bot": df["High"].iloc[i-2]})
        elif df["High"].iloc[i] < df["Low"].iloc[i-2]:
            fvgs.append({"t": "bear", "top": df["Low"].iloc[i-2], "bot": df["High"].iloc[i]})
    return fvgs[-15:]

def detect_ob(df):
    obs = []
    for i in range(1, len(df) - 2):
        if (df["Close"].iloc[i] < df["Open"].iloc[i] and
                df["Close"].iloc[i+1] > df["Open"].iloc[i+1] and
                df["Close"].iloc[i+1] > df["High"].iloc[i]):
            obs.append({"t": "bull", "top": df["High"].iloc[i], "bot": df["Low"].iloc[i]})
        elif (df["Close"].iloc[i] > df["Open"].iloc[i] and
                df["Close"].iloc[i+1] < df["Open"].iloc[i+1] and
                df["Close"].iloc[i+1] < df["Low"].iloc[i]):
            obs.append({"t": "bear", "top": df["High"].iloc[i], "bot": df["Low"].iloc[i]})
    return obs[-15:]

def run_ta(df):
    c = df["Close"]; h = df["High"]; l = df["Low"]; v = df["Volume"]
    ta = {}

    ta["e9"]   = calc_ema(c, 9)
    ta["e20"]  = calc_ema(c, 20)
    ta["e50"]  = calc_ema(c, 50)
    ta["e200"] = calc_ema(c, 200)
    ta["rsi"]  = calc_rsi(c)
    ta["ml"], ta["sl_"], ta["hist"] = calc_macd(c)
    ta["k"], ta["d_"] = calc_stoch(h, l, c)
    ta["atr"]  = calc_atr(h, l, c)
    ta["bb_up"], ta["bb_mid"], ta["bb_lo"] = calc_bb(c)
    ta["vm20"] = calc_sma(v, 20)
    try:
        ta["vwap"] = calc_vwap(df)
    except Exception:
        ta["vwap"] = c.copy()

    def last(s):
        v2 = s.iloc[-1]
        return float(v2) if not (isinstance(v2, float) and np.isnan(v2)) else 0.0

    p = last(c); ta["p"] = p
    ta["e9v"]   = last(ta["e9"])
    ta["e20v"]  = last(ta["e20"])
    ta["e50v"]  = last(ta["e50"])
    ta["e200v"] = last(ta["e200"])
    ta["rsi_v"] = last(ta["rsi"])
    ta["ml_v"]  = last(ta["ml"])
    ta["sl_v"]  = last(ta["sl_"])
    ta["hist_v"]= last(ta["hist"])
    ta["atr_v"] = last(ta["atr"])
    ta["bb_up_v"] = last(ta["bb_up"])
    ta["bb_lo_v"] = last(ta["bb_lo"])
    ta["bb_mid_v"]= last(ta["bb_mid"])
    ta["k_v"]   = last(ta["k"]) or 50.0
    ta["d_v"]   = last(ta["d_"]) or 50.0
    ta["vwap_v"]= last(ta["vwap"]) or p

    cv = last(v); avm = last(ta["vm20"]) or 1.0
    ta["cv"] = cv; ta["avm"] = avm
    ta["vr"] = cv / avm if avm > 0 else 1.0

    lb = min(60, len(df))
    fh = float(h.iloc[-lb:].max()); fl = float(l.iloc[-lb:].min())
    ta["fh"] = fh; ta["fl"] = fl; ta["fibs"] = calc_fib(fh, fl)

    ta["ph"], ta["pl"] = calc_pivots(h, l)
    ta["sup"] = sorted([x[1] for x in ta["pl"][-5:]])
    ta["res"] = sorted([x[1] for x in ta["ph"][-5:]], reverse=True)

    ta["fvgs"] = detect_fvg(df)
    ta["obs"]  = detect_ob(df)

    # 20-day range for sweep detection
    h20 = float(h.iloc[-20:].max()); l20 = float(l.iloc[-20:].min())
    ta["h20"] = h20; ta["l20"] = l20
    r3 = df.iloc[-4:]
    ta["swept_lo"] = bool(any(r3["Low"]  <= l20 * 1.003))
    ta["swept_hi"] = bool(any(r3["High"] >= h20 * 0.997))

    # FVG proximity
    ta["in_bull_fvg"] = any(f["t"]=="bull" and f["bot"] <= p <= f["top"] for f in ta["fvgs"])
    ta["in_bear_fvg"] = any(f["t"]=="bear" and f["bot"] <= p <= f["top"] for f in ta["fvgs"])
    ta["at_bull_ob"]  = any(o["t"]=="bull" and o["bot"]*(1-.008)<=p<=o["top"]*(1+.008) for o in ta["obs"])
    ta["at_bear_ob"]  = any(o["t"]=="bear" and o["bot"]*(1-.008)<=p<=o["top"]*(1+.008) for o in ta["obs"])

    # Crossovers (last 4 bars)
    e50a = ta["e50"].values; e200a = ta["e200"].values
    mla  = ta["ml"].values;  sla   = ta["sl_"].values
    n_cross = min(4, len(e50a) - 1)
    ta["golden"] = bool(e50a[-n_cross] <= e200a[-n_cross] and e50a[-1] > e200a[-1])
    ta["death"]  = bool(e50a[-n_cross] >= e200a[-n_cross] and e50a[-1] < e200a[-1])
    ta["macd_bull"] = bool(mla[-n_cross] <= sla[-n_cross] and mla[-1] > sla[-1])
    ta["macd_bear"] = bool(mla[-n_cross] >= sla[-n_cross] and mla[-1] < sla[-1])

    # Divergence (20-bar)
    rc = c.iloc[-20:]; rm = ta["ml"].iloc[-20:]
    ta["bull_div"] = bool(len(rc) >= 10 and rc.iloc[-1] < rc.iloc[0] and rm.iloc[-1] > rm.iloc[0])
    ta["bear_div"] = bool(len(rc) >= 10 and rc.iloc[-1] > rc.iloc[0] and rm.iloc[-1] < rm.iloc[0])

    # Fibonacci proximity (within 1.5%)
    ta["at_618"] = any(abs(p-v2)/max(p,1e-10)<.015 for k2,v2 in ta["fibs"].items() if "0.618" in k2)
    ta["at_786"] = any(abs(p-v2)/max(p,1e-10)<.015 for k2,v2 in ta["fibs"].items() if "0.786" in k2)
    ta["at_382"] = any(abs(p-v2)/max(p,1e-10)<.015 for k2,v2 in ta["fibs"].items() if "0.382" in k2)

    # Bollinger
    ta["at_bb_lo"] = p <= ta["bb_lo_v"] * 1.012
    ta["at_bb_up"] = p >= ta["bb_up_v"] * 0.988
    bb_width = (ta["bb_up_v"] - ta["bb_lo_v"]) / max(ta["bb_mid_v"], 1e-10)
    ta["bb_squeeze"] = bb_width < 0.05

    # VWAP
    ta["above_vwap"] = p > ta["vwap_v"]

    # Trend
    e50v = ta["e50v"]; e200v = ta["e200v"]
    if p > e50v > e200v:    ta["trend"] = "Bullish"
    elif p < e50v < e200v:  ta["trend"] = "Bearish"
    elif p > e200v:          ta["trend"] = "Neutral-Bullish"
    else:                    ta["trend"] = "Neutral-Bearish"
    ta["mom"] = "Strong" if abs(ta["rsi_v"] - 50) > 15 else "Weak"

    # Nearest levels
    sl2 = [x for x in ta["sup"] if x < p]
    rl2 = [x for x in ta["res"] if x > p]
    ta["near_sup"] = max(sl2) if sl2 else ta["fl"]
    ta["near_res"] = min(rl2) if rl2 else ta["fh"]

    # Price changes
    ta["chg1d"] = float((c.iloc[-1]/c.iloc[-2]-1)*100) if len(c)>1 else 0.0
    ta["chg5d"] = float((c.iloc[-1]/c.iloc[-6]-1)*100) if len(c)>5 else 0.0
    return ta

# ─────────────────────────────────────────────────────────────
# 8 STRATEGIES
# ─────────────────────────────────────────────────────────────
def run_strategies(ta):
    p = ta["p"]; rv = ta["rsi_v"]
    e50 = ta["e50v"]; e200 = ta["e200v"]; vr = ta["vr"]
    R = {}

    # 1. PELOSI-LIQUIDITY CONFLUENCE
    if ta["swept_lo"] and (ta["in_bull_fvg"] or ta["at_bull_ob"]) and p > e50:
        v="BUY"; d="Swept low ✓ | Bull FVG/OB ✓ | Above EMA50 ✓"
    elif ta["swept_hi"] and (ta["in_bear_fvg"] or ta["at_bear_ob"]) and p < e50:
        v="SELL"; d="Swept high ✓ | Bear FVG/OB ✓ | Below EMA50 ✓"
    elif ta["swept_lo"] and rv < 42:
        v="BUY"; d=f"Liquidity sweep low ✓ | RSI {rv:.1f}"
    elif ta["swept_hi"] and rv > 58:
        v="SELL"; d=f"Liquidity sweep high ✓ | RSI {rv:.1f}"
    elif ta["in_bull_fvg"] and p > e200:
        v="BUY"; d="In bullish FVG ✓ | Above EMA200"
    elif ta["in_bear_fvg"] and p < e200:
        v="SELL"; d="In bearish FVG ✓ | Below EMA200"
    else:
        v="HOLD"; d="No sweep + FVG/OB confluence"
    R["s1"] = {"vote":v,"name":"Pelosi-Liquidity Confluence","detail":d}

    # 2. EMA CROSSOVER + RSI
    bull = (ta["golden"] or (p>e50>e200 and e50>e200*1.002))
    bear = (ta["death"]  or (p<e50<e200 and e200>e50*1.002))
    if bull and 25 <= rv <= 72:
        v="BUY"; d=f"EMA50>EMA200 ✓ | RSI {rv:.1f} neutral"
    elif bear and 28 <= rv <= 75:
        v="SELL"; d=f"EMA50<EMA200 ✓ | RSI {rv:.1f}"
    elif rv < 28:
        v="BUY"; d=f"RSI oversold {rv:.1f} — bounce zone"
    elif rv > 72:
        v="SELL"; d=f"RSI overbought {rv:.1f} — reversal risk"
    elif bull:
        v="BUY"; d=f"EMA50 > EMA200 | RSI {rv:.1f}"
    elif bear:
        v="SELL"; d=f"EMA50 < EMA200 | RSI {rv:.1f}"
    else:
        v="HOLD"; d=f"EMAs mixed | RSI {rv:.1f}"
    R["s2"] = {"vote":v,"name":"EMA Crossover + RSI","detail":d}

    # 3. LIQUIDITY SWEEP + ORDER BLOCK
    if ta["swept_lo"] and ta["at_bull_ob"]:
        v="BUY"; d="Swept low + at bullish OB — prime entry"
    elif ta["swept_hi"] and ta["at_bear_ob"]:
        v="SELL"; d="Swept high + at bearish OB — prime short"
    elif ta["at_bull_ob"] and p > e50:
        v="BUY"; d="At bullish OB above EMA50"
    elif ta["at_bear_ob"] and p < e50:
        v="SELL"; d="At bearish OB below EMA50"
    elif ta["swept_lo"]:
        v="BUY"; d="20D low swept — watching for OB bounce"
    elif ta["swept_hi"]:
        v="SELL"; d="20D high swept — watching for OB rejection"
    else:
        v="HOLD"; d="No active sweep or OB signal"
    R["s3"] = {"vote":v,"name":"Liquidity Sweep + Order Block","detail":d}

    # 4. MACD DIVERGENCE
    if ta["bull_div"] or ta["macd_bull"]:
        lbl = "Bullish divergence" if ta["bull_div"] else "MACD bull crossover"
        v="BUY"; d=f"{lbl} | Hist {ta['hist_v']:.5f}"
    elif ta["bear_div"] or ta["macd_bear"]:
        lbl = "Bearish divergence" if ta["bear_div"] else "MACD bear crossover"
        v="SELL"; d=f"{lbl} | Hist {ta['hist_v']:.5f}"
    elif ta["hist_v"] > 0 and ta["ml_v"] > ta["sl_v"]:
        v="BUY"; d=f"MACD above signal | +{ta['hist_v']:.5f}"
    elif ta["hist_v"] < 0 and ta["ml_v"] < ta["sl_v"]:
        v="SELL"; d=f"MACD below signal | {ta['hist_v']:.5f}"
    else:
        v="HOLD"; d="No MACD divergence signal"
    R["s4"] = {"vote":v,"name":"MACD Divergence","detail":d}

    # 5. VOLUME + FIBONACCI
    at_fib = ta["at_618"] or ta["at_786"] or ta["at_382"]
    if at_fib and vr > 1.25 and rv < 42:
        v="BUY"; d=f"Fib level ✓ | Vol {vr:.1f}x | RSI {rv:.1f} low"
    elif at_fib and vr > 1.25 and rv > 58:
        v="SELL"; d=f"Fib level ✓ | Vol {vr:.1f}x | RSI {rv:.1f} high"
    elif vr > 1.5 and p > e50 and rv < 55:
        v="BUY"; d=f"High vol {vr:.1f}x | Above EMA50"
    elif vr > 1.5 and p < e50 and rv > 48:
        v="SELL"; d=f"High vol {vr:.1f}x | Below EMA50"
    elif at_fib and p > e200:
        v="BUY"; d=f"At Fib zone | Above EMA200"
    else:
        v="HOLD"; d=f"Vol {vr:.1f}x avg | No Fib+vol confluence"
    R["s5"] = {"vote":v,"name":"Volume + Fibonacci","detail":d}

    # 6. BOLLINGER BAND
    if ta["at_bb_lo"] and rv < 40:
        v="BUY"; d=f"At lower BB | RSI {rv:.1f} — mean reversion"
    elif ta["at_bb_up"] and rv > 60:
        v="SELL"; d=f"At upper BB | RSI {rv:.1f} — overextended"
    elif ta["bb_squeeze"] and vr > 1.25:
        v = "BUY" if p > ta["bb_mid_v"] else "SELL"
        d = f"BB squeeze breakout | Vol {vr:.1f}x — {'upside' if v=='BUY' else 'downside'}"
    elif p > ta["bb_up_v"] and rv < 70:
        v="BUY"; d="Above upper BB — strong momentum"
    elif p < ta["bb_lo_v"] and rv > 30:
        v="SELL"; d="Below lower BB — strong selling pressure"
    else:
        v="HOLD"; d="Within BB range — no breakout"
    R["s6"] = {"vote":v,"name":"Bollinger Band Signal","detail":d}

    # 7. VWAP + STOCHASTIC
    kv = ta["k_v"]; dv = ta["d_v"]
    if ta["above_vwap"] and kv < 25:
        v="BUY"; d=f"Above VWAP | Stoch {kv:.1f} oversold"
    elif not ta["above_vwap"] and kv > 75:
        v="SELL"; d=f"Below VWAP | Stoch {kv:.1f} overbought"
    elif ta["above_vwap"] and kv > dv and kv < 75:
        v="BUY"; d=f"Above VWAP ✓ | Stoch K crossing up {kv:.1f}"
    elif not ta["above_vwap"] and kv < dv and kv > 25:
        v="SELL"; d=f"Below VWAP | Stoch K crossing down {kv:.1f}"
    elif ta["above_vwap"] and p > e50:
        v="BUY"; d=f"Above VWAP + EMA50 | Stoch {kv:.1f}"
    else:
        v="HOLD"; d=f"VWAP {'above' if ta['above_vwap'] else 'below'} | Stoch {kv:.1f}"
    R["s7"] = {"vote":v,"name":"VWAP + Stochastic","detail":d}

    # 8. EMA STACK TREND STRENGTH
    atr_pct = ta["atr_v"] / max(p, 1e-10) * 100
    e9v = ta["e9v"]; e20v = ta["e20v"]
    if p > e9v > e20v > e50 > e200 and atr_pct > 0.25:
        v="BUY"; d=f"Full bull EMA stack ✓ | ATR {atr_pct:.1f}%"
    elif p < e9v < e20v < e50 < e200 and atr_pct > 0.25:
        v="SELL"; d=f"Full bear EMA stack ✓ | ATR {atr_pct:.1f}%"
    elif p > e50 > e200:
        v="BUY"; d=f"EMA50/200 bullish alignment | ATR {atr_pct:.1f}%"
    elif p < e50 < e200:
        v="SELL"; d=f"EMA50/200 bearish alignment | ATR {atr_pct:.1f}%"
    elif atr_pct < 0.15:
        v="HOLD"; d=f"Low ATR {atr_pct:.2f}% — consolidation phase"
    else:
        v="HOLD"; d=f"Mixed EMA alignment | ATR {atr_pct:.1f}%"
    R["s8"] = {"vote":v,"name":"EMA Stack + Trend Strength","detail":d}

    return R

# ─────────────────────────────────────────────────────────────
# WIN PROBABILITY
# ─────────────────────────────────────────────────────────────
def calc_win_prob(strats, ta, sent, votes):
    bn = votes["BUY"]; sn = votes["SELL"]
    if bn + sn == 0: return 50.0
    mx = max(bn, sn)
    base = 0.47 + (mx / 8) * 0.29
    rv = ta["rsi_v"]; p = ta["p"]; e50 = ta["e50v"]; e200 = ta["e200v"]
    rsi_f = 0.04 if (bn>sn and rv<62) or (sn>bn and rv>38) else 0
    if rv < 27 or rv > 73: rsi_f += 0.03
    ema_f = 0.06 if (bn>sn and p>e50>e200) or (sn>bn and p<e50<e200) else 0
    vol_f = min(0.04, (ta["vr"]-1)*0.025) if ta["vr"] > 1 else 0
    sent_f = 0.03 if (sent=="positive" and bn>sn) or (sent=="negative" and sn>bn) else 0
    smc_f  = 0.05 if (ta["in_bull_fvg"] and bn>sn) or (ta["in_bear_fvg"] and sn>bn) else 0
    smc_f += 0.03 if (ta["at_bull_ob"] and bn>sn) or (ta["at_bear_ob"] and sn>bn) else 0
    vwap_f = 0.03 if (ta["above_vwap"] and bn>sn) or (not ta["above_vwap"] and sn>bn) else 0
    total = base + rsi_f + ema_f + vol_f + sent_f + smc_f + vwap_f
    return round(min(0.93, max(0.40, total)) * 100, 1)

# ─────────────────────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────────────────────
def build_chart(df, ta, ticker):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.50, 0.17, 0.17, 0.16],
        subplot_titles=[f"{ticker} · Price + EMAs + Bollinger",
                        "Volume", "RSI (14) · Stochastic", "MACD"]
    )
    c=df["Close"]; o=df["Open"]; h=df["High"]; l_=df["Low"]; v=df["Volume"]

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=o, high=h, low=l_, close=c,
        increasing_line_color="#00d4aa", decreasing_line_color="#ff4d6d",
        increasing_fillcolor="rgba(0,212,170,0.55)",
        decreasing_fillcolor="rgba(255,77,109,0.55)",
        name="Price", showlegend=False
    ), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=ta["bb_up"], name="BB Upper",
        line=dict(color="rgba(167,139,250,0.4)", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ta["bb_lo"], name="BB Lower",
        line=dict(color="rgba(167,139,250,0.4)", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(167,139,250,0.04)", showlegend=False), row=1, col=1)

    # EMAs
    for series, name, color, dash in [
        (ta["e200"], "EMA 200", "#4d9fff", "dot"),
        (ta["e50"],  "EMA 50",  "#c9a84c", "solid"),
        (ta["e20"],  "EMA 20",  "rgba(0,212,170,0.55)", "dash"),
    ]:
        fig.add_trace(go.Scatter(x=df.index, y=series, name=name,
            line=dict(color=color, width=1.7, dash=dash)), row=1, col=1)

    # VWAP
    fig.add_trace(go.Scatter(x=df.index, y=ta["vwap"], name="VWAP",
        line=dict(color="rgba(255,200,100,0.45)", width=1, dash="dot")), row=1, col=1)

    # Fibonacci
    for fname, flevel in ta["fibs"].items():
        c2 = "#c9a84c" if any(x in fname for x in ["0.618","0.786"]) else "rgba(201,168,76,0.2)"
        fig.add_hline(y=flevel, line_dash="dot", line_color=c2, line_width=0.7,
                      annotation_text=fname, annotation_position="right",
                      annotation_font_size=8, annotation_font_color=c2, row=1, col=1)

    # Support / Resistance
    for s2 in ta["sup"][-3:]:
        fig.add_hline(y=s2, line_dash="dot", line_color="rgba(0,212,170,0.3)", line_width=0.8, row=1, col=1)
    for r2 in ta["res"][-3:]:
        fig.add_hline(y=r2, line_dash="dot", line_color="rgba(255,77,109,0.3)", line_width=0.8, row=1, col=1)

    # Volume
    vcol = ["rgba(0,212,170,0.5)" if cv >= ov else "rgba(255,77,109,0.5)"
            for cv, ov in zip(c, o)]
    fig.add_trace(go.Bar(x=df.index, y=v, marker_color=vcol, name="Volume", showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ta["vm20"], name="Vol MA20",
        line=dict(color="#c9a84c", width=1.2)), row=2, col=1)

    # RSI + Stochastic
    fig.add_trace(go.Scatter(x=df.index, y=ta["rsi"], name="RSI 14",
        line=dict(color="#a78bfa", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ta["k"], name="Stoch K",
        line=dict(color="rgba(0,212,170,0.6)", width=1, dash="dot")), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,77,109,0.45)", line_width=0.8, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,212,170,0.45)", line_width=0.8, row=3, col=1)

    # MACD
    mcolors = ["rgba(0,212,170,0.5)" if hv >= 0 else "rgba(255,77,109,0.5)" for hv in ta["hist"]]
    fig.add_trace(go.Bar(x=df.index, y=ta["hist"], marker_color=mcolors, name="MACD Hist"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ta["ml"], name="MACD",
        line=dict(color="#00d4aa", width=1.3)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ta["sl_"], name="Signal",
        line=dict(color="#ff4d6d", width=1.3)), row=4, col=1)

    fig.update_layout(
        paper_bgcolor="#08090d", plot_bgcolor="#08090d",
        font=dict(family="Space Mono", color="#8892a4", size=9),
        legend=dict(bgcolor="rgba(14,17,24,0.9)", bordercolor="rgba(255,255,255,0.06)",
                    borderwidth=1, font=dict(size=9), x=0.01, y=0.99),
        xaxis_rangeslider_visible=False, height=750,
        margin=dict(l=5, r=85, t=35, b=5)
    )
    for i in range(1, 5):
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", showgrid=True,
                         zeroline=False, row=i, col=1, tickfont=dict(size=8))
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", showgrid=True,
                         zeroline=False, row=i, col=1, tickfont=dict(size=8))
    for ann in fig["layout"]["annotations"]:
        ann["font"]["size"] = 8
        ann["font"]["color"] = "#4a5568"
    return fig

# ─────────────────────────────────────────────────────────────
# RECOMMENDATION GENERATOR
# ─────────────────────────────────────────────────────────────
def gen_reco(ticker, ta, votes, sent, wp, strats):
    bn=votes["BUY"]; sn=votes["SELL"]; hn=votes["HOLD"]
    p=ta["p"]; rv=ta["rsi_v"]; vr=ta["vr"]
    direction = "BUY" if bn>sn else "SELL" if sn>bn else "HOLD"
    mx = max(bn, sn, hn)
    if mx>=6 and wp>=74:   risk="LOW"
    elif mx>=5 and wp>=68: risk="LOW-MEDIUM"
    elif mx>=4 and wp>=62: risk="MEDIUM"
    elif mx>=3:            risk="MEDIUM-HIGH"
    else:                  risk="HIGH"
    ps_map={"LOW":"1.5–2.0%","LOW-MEDIUM":"1.0–1.5%","MEDIUM":"0.5–1.0%","MEDIUM-HIGH":"0.25–0.5%","HIGH":"≤0.25%"}
    pos_sz = ps_map[risk]
    atr_v = ta["atr_v"]
    if direction=="BUY":
        sl = max(ta["near_sup"]*0.997, p-atr_v*1.8)
        tp1 = p + (p-sl)*1.5
        tp2 = min(ta["near_res"], p+atr_v*4)
    elif direction=="SELL":
        sl = min(ta["near_res"]*1.003, p+atr_v*1.8)
        tp1 = p - (sl-p)*1.5
        tp2 = max(ta["near_sup"], p-atr_v*4)
    else:
        sl = p - atr_v*2; tp1 = p + atr_v*2; tp2 = ta["near_res"]
    rr = abs(tp1-p)/max(abs(p-sl), 1e-10)
    conf = round(wp/10, 1)
    top_names = [s["name"] for s in strats.values() if s["vote"]==direction][:3]
    s_names = ", ".join(top_names) if top_names else "none"
    sent_w = ("supportive" if (sent=="positive" and direction=="BUY") or
              (sent=="negative" and direction=="SELL") else
              "conflicting" if (sent=="negative" and direction=="BUY") or
              (sent=="positive" and direction=="SELL") else "neutral")
    psl=(sl-p)/p*100; ptp1=(tp1-p)/p*100; ptp2=(tp2-p)/p*100
    p1 = (f"Across <strong>8 independent strategy systems</strong>, the final vote is "
          f"<strong>{bn} BUY · {sn} SELL · {hn} HOLD</strong>, yielding a clear "
          f"<strong>{direction}</strong> signal. Confirming strategies: <strong>{s_names}</strong>. "
          f"News sentiment is <strong>{sent}</strong> and is {sent_w} for this direction.")
    p2 = (f"Price is <strong>{'above' if p>ta['e50v'] else 'below'} EMA-50</strong> and "
          f"<strong>{'above' if p>ta['e200v'] else 'below'} EMA-200</strong>. "
          f"RSI: <strong>{rv:.1f}</strong> "
          f"({'overbought' if rv>70 else 'oversold' if rv<30 else 'neutral'}). "
          f"Volume: <strong>{vr:.2f}× the 20-period average</strong>. "
          f"Bollinger: <strong>{'lower band — oversold' if ta['at_bb_lo'] else 'upper band — overextended' if ta['at_bb_up'] else 'normal range'}</strong>. "
          f"VWAP: <strong>{'above' if ta['above_vwap'] else 'below'}</strong>. "
          f"Overall trend: <strong>{ta['trend']}</strong>. Risk level: <strong>{risk}</strong>.")
    p3 = (f"<strong>Stop Loss: {ps(sl)} ({psl:+.1f}%)</strong> — "
          f"set at {'support' if direction=='BUY' else 'resistance'} with 1.8× ATR buffer. "
          f"<strong>TP1: {ps(tp1)} ({ptp1:+.1f}%)</strong> — close 50% here, move SL to breakeven. "
          f"<strong>TP2: {ps(tp2)} ({ptp2:+.1f}%)</strong> — trail the remainder with EMA20. "
          f"Risk/Reward: <strong>1:{rr:.1f}</strong>. "
          f"Recommended position: <strong>{pos_sz} of capital</strong>. "
          f"Confidence score: <strong>{conf}/10</strong>.")
    return {"dir":direction,"risk":risk,"pos":pos_sz,"sl":sl,"tp1":tp1,"tp2":tp2,
            "rr":rr,"conf":conf,"paras":[p1,p2,p3]}

# ─────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────
def render_strats(strats):
    html = ""
    for s in strats.values():
        html += (f'<div class="sr">'
                 f'<div class="sn">{s["name"]}</div>'
                 f'<div class="sd">{s["detail"]}</div>'
                 f'{badge(s["vote"])}</div>')
    st.markdown(html, unsafe_allow_html=True)

def render_news(headlines):
    if not headlines:
        st.markdown('<p style="color:var(--t3);font-size:.82rem;">No headlines found. '
                    'Set FINNHUB_API_KEY env variable for richer news coverage.</p>',
                    unsafe_allow_html=True)
        return
    html = ""
    for h in headlines[:10]:
        s = sent_score(h)
        dc = {"positive":"npos","negative":"nneg","neutral":"nneut"}[s]
        sc = {"positive":"spos","negative":"sneg","neutral":"sneut"}[s]
        html += (f'<div class="ni">'
                 f'<div class="nd {dc}"></div>'
                 f'<div class="nh">{h}</div>'
                 f'<div class="ns {sc}">{s.upper()}</div></div>')
    st.markdown(html, unsafe_allow_html=True)

def render_fib(fibs, p):
    rows = ""
    for name, level in fibs.items():
        pct_from = (level - p) / p * 100
        key = any(x in name for x in ["0.618","0.786","0.382"])
        gs = "color:var(--gold);" if key else ""
        pc = "color:var(--teal);" if pct_from < 0 else "color:var(--red);"
        rows += (f'<tr style="border-bottom:1px solid var(--border)">'
                 f'<td style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.7rem;{gs}">{name}</td>'
                 f'<td style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.76rem;">{ps(level)}</td>'
                 f'<td style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.7rem;{pc}">{pct_from:+.2f}%</td>'
                 f'</tr>')
    hdr = ('<table style="width:100%;border-collapse:collapse">'
           '<thead><tr style="border-bottom:1px solid var(--border)">'
           '<th style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.15em;color:var(--t3);text-align:left">LEVEL</th>'
           '<th style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.15em;color:var(--t3);text-align:left">PRICE</th>'
           '<th style="padding:.42rem .65rem;font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.15em;color:var(--t3);text-align:left">FROM NOW</th>'
           '</tr></thead>')
    st.markdown(hdr + f'<tbody>{rows}</tbody></table>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────

# Search panel
st.markdown("""
<div style="background:var(--bg2);border:1px solid var(--border);border-radius:4px;
  padding:1.8rem 2rem 1.4rem;margin-bottom:1.5rem;">
<p style="font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.2em;
  color:var(--t3);text-transform:uppercase;margin-bottom:.65rem;">
  ◈ UNIVERSAL ENGINE · TYPE ANY STOCK NAME, CRYPTO, OR TICKER · AUTO-SUGGESTIONS APPEAR BELOW
</p>""", unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])
with c1:
    query = st.text_input(
        "", placeholder="e.g.  Apple  ·  NVDA  ·  Bitcoin  ·  BTC  ·  Tesla  ·  ETH  ·  Samsung  ·  SPY",
        label_visibility="collapsed", key="search_q"
    )
with c2:
    st.markdown("<div style='height:.35rem'></div>", unsafe_allow_html=True)
    go_btn = st.button("⬡  ANALYZE", use_container_width=True)

# Live suggestions
final_ticker = None

if query and len(query.strip()) >= 2 and not go_btn:
    with st.spinner("Searching…"):
        suggestions = search_markets(query.strip())
    if suggestions:
        opts = [f"{s['sym']} — {s['name']} [{s['exch']}]" for s in suggestions]
        chosen = st.selectbox("📌 Select from results below:", opts, key="chosen_sel")
        if st.button("▶  Analyze Selected", key="analyze_sel_btn"):
            final_ticker = chosen.split(" — ")[0].strip()
            st.session_state["pending_ticker"] = final_ticker
            st.rerun()
    else:
        st.caption("No results found. Try a different name or ticker.")

st.markdown("""
<p style="font-family:'Space Mono',monospace;font-size:.54rem;color:var(--t3);margin-top:.65rem;">
  Covers every stock on NYSE · NASDAQ · LSE · TSX · ASX · Crypto (1,000s via CoinGecko) · ETFs · Indices
</p></div>""", unsafe_allow_html=True)

# Resolve final ticker
if go_btn and query.strip():
    final_ticker = query.strip().upper()
elif "pending_ticker" in st.session_state:
    final_ticker = st.session_state.pop("pending_ticker")

# ─────────────────────────────────────────────────────────────
# FULL ANALYSIS
# ─────────────────────────────────────────────────────────────
if final_ticker:
    ticker = final_ticker.upper().strip()

    # ── Step 1: Detect asset type ─────────────────────────
    status_placeholder = st.empty()
    status_placeholder.markdown(
        f'<div class="status-warn">⟳ Detecting asset type for {ticker}…</div>',
        unsafe_allow_html=True
    )
    asset_type = detect_type(ticker)

    # ── Step 2: Fetch data (with smart fallback) ──────────
    df = None; meta = {}; coin_id = ""; coin_name = ""

    if asset_type == "crypto":
        status_placeholder.markdown(
            f'<div class="status-warn">⟳ Fetching {ticker} from CoinGecko…</div>',
            unsafe_allow_html=True
        )
        coin_id = resolve_coin_id(ticker)
        df, ferr = fetch_crypto_data(coin_id)
        if df is not None:
            meta = fetch_crypto_meta(coin_id)
            coin_name = meta.get("name", ticker)
        else:
            # Fallback: try Yahoo Finance with -USD suffix
            status_placeholder.markdown(
                f'<div class="status-warn">⟳ CoinGecko failed, trying Yahoo Finance ({ticker}-USD)…</div>',
                unsafe_allow_html=True
            )
            df, meta, _ = fetch_stock_data(ticker + "-USD")
            if df is not None:
                asset_type = "stock"
    else:
        status_placeholder.markdown(
            f'<div class="status-warn">⟳ Fetching {ticker} from Yahoo Finance…</div>',
            unsafe_allow_html=True
        )
        df, meta, ferr = fetch_stock_data(ticker)
        if df is None:
            # Fallback: maybe user typed a crypto symbol
            status_placeholder.markdown(
                f'<div class="status-warn">⟳ Yahoo Finance failed, trying CoinGecko for {ticker}…</div>',
                unsafe_allow_html=True
            )
            coin_id = resolve_coin_id(ticker.lower())
            df2, ferr2 = fetch_crypto_data(coin_id)
            if df2 is not None:
                df = df2; asset_type = "crypto"
                meta = fetch_crypto_meta(coin_id)
                coin_name = meta.get("name", ticker)

    # ── Step 3: Validate ──────────────────────────────────
    if df is None or len(df) < 15:
        status_placeholder.empty()
        st.error(f"""
### ❌ No data found for **{ticker}**

**Most common fixes:**

1. **Use the search box** — type 2+ characters and select from the dropdown list. This always gives the correct ticker format.
2. **International stocks** need exchange suffix:
   - London: `BARC.L` · Toronto: `RY.TO` · Germany: `SAP.DE` · Japan: `7203.T`
   - Australia: `BHP.AX` · Hong Kong: `0700.HK`
3. **Crypto** — type the symbol (e.g. `BTC`, `ETH`, `SOL`) or the full name (e.g. `Bitcoin`)
4. **CoinGecko rate limit** — if a crypto worked before but fails now, wait 30 seconds then retry
5. **US stocks** — use standard tickers: `AAPL`, `NVDA`, `TSLA`, `META`, `AMZN`, `MSFT`

**Currently tried:** `{ticker}` as {'crypto' if asset_type == 'crypto' else 'stock'}
        """)
        st.stop()

    status_placeholder.markdown(
        f'<div class="status-ok">✓ Data loaded · {len(df)} daily candles · Running 8-strategy analysis…</div>',
        unsafe_allow_html=True
    )

    # ── Step 4: Analysis ──────────────────────────────────
    ta = run_ta(df)
    news = fetch_news(ticker, asset_type, coin_name)
    sent_label, _ = agg_sentiment(news)
    strats = run_strategies(ta)

    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for s in strats.values():
        votes[s["vote"]] += 1

    wp_val = calc_win_prob(strats, ta, sent_label, votes)
    reco   = gen_reco(ticker, ta, votes, sent_label, wp_val, strats)
    p = ta["p"]
    status_placeholder.empty()

    # ── TICKER HEADER ────────────────────────────────────
    chg  = ta["chg1d"]; chg5 = ta["chg5d"]
    cc   = "up" if chg >= 0 else "dn"
    dc   = {"BUY":"var(--teal)","SELL":"var(--red)","HOLD":"var(--blue)"}.get(reco["dir"],"var(--blue)")
    dname = coin_name if (asset_type=="crypto" and coin_name) else sg(meta,"longName",ticker) or ticker

    st.markdown(f"""
    <div style="display:flex;align-items:flex-end;justify-content:space-between;
        padding:1.4rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1.4rem;">
      <div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3.2rem;letter-spacing:.05em;line-height:1;">{ticker}</div>
        <div style="font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.18em;
            color:var(--t3);text-transform:uppercase;margin-top:.2rem;">
          {str(dname)[:55]} · {'CRYPTOCURRENCY' if asset_type=='crypto' else 'EQUITY / ETF'}
        </div>
      </div>
      <div style="text-align:right;">
        <div style="font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;line-height:1;">{ps(p)}</div>
        <div class="{cc}" style="font-family:'Space Mono',monospace;font-size:.78rem;margin-top:.2rem;">
          {chg:+.2f}% today &nbsp;·&nbsp; {chg5:+.2f}% 5D
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── METRIC TILES ─────────────────────────────────────
    th = '<div class="mg">'
    rv = ta["rsi_v"]
    th += mtile("RSI (14)", f"{rv:.1f}",
                "Overbought" if rv>70 else "Oversold" if rv<30 else "Neutral",
                "dn" if rv>70 else "up" if rv<30 else "")
    th += mtile("EMA 50", ps(ta["e50v"]),
                "Above ✓" if p>ta["e50v"] else "Below ✗", "up" if p>ta["e50v"] else "dn")
    th += mtile("EMA 200", ps(ta["e200v"]),
                "Bullish" if p>ta["e200v"] else "Bearish", "up" if p>ta["e200v"] else "dn")
    th += mtile("Volume", f"{ta['vr']:.2f}×",
                "High" if ta["vr"]>1.5 else "Normal" if ta["vr"]>0.7 else "Low",
                "up" if ta["vr"]>1.5 else "")
    th += mtile("MACD Hist", f"{ta['hist_v']:.5f}",
                "Bullish" if ta["hist_v"]>0 else "Bearish", "up" if ta["hist_v"]>0 else "dn")
    th += mtile("VWAP", ps(ta["vwap_v"]),
                "Above ✓" if ta["above_vwap"] else "Below ✗", "up" if ta["above_vwap"] else "dn")
    th += mtile("Stochastic K", f"{ta['k_v']:.1f}",
                "Overbought" if ta["k_v"]>80 else "Oversold" if ta["k_v"]<20 else "Neutral",
                "dn" if ta["k_v"]>80 else "up" if ta["k_v"]<20 else "")
    th += mtile("ATR", ps(ta["atr_v"]), f"{ta['atr_v']/p*100:.2f}% of price")

    if asset_type == "stock":
        th += mtile("Market Cap", fmt(sg(meta,"marketCap"), "$"))
        th += mtile("P/E Ratio", f'{sg(meta,"trailingPE"):.1f}' if sg(meta,"trailingPE") else "N/A")
        th += mtile("52W High",  ps(sg(meta,"fiftyTwoWeekHigh")))
    else:
        md = meta.get("market_data", {})
        th += mtile("Market Cap", fmt(md.get("market_cap",{}).get("usd"), "$"))
        th += mtile("24h Volume", fmt(md.get("total_volume",{}).get("usd"), "$"))
        th += mtile("CMC Rank", f'#{meta.get("market_cap_rank","N/A")}')
    th += mtile("Trend", ta["trend"])
    th += "</div>"
    st.markdown(th, unsafe_allow_html=True)

    # ── CHART ────────────────────────────────────────────
    divider("PRICE ACTION · EMAs · BOLLINGER · VWAP · FIBONACCI · RSI · STOCH · MACD")
    fig = build_chart(df, ta, ticker)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── LEFT / RIGHT COLUMNS ─────────────────────────────
    col_l, col_r = st.columns([1, 1], gap="medium")

    with col_l:
        # Technical Summary
        st.markdown('<div class="card ca-teal">', unsafe_allow_html=True)
        st.markdown('<div class="ct">⬡ TECHNICAL SUMMARY</div>', unsafe_allow_html=True)
        sups_html = "".join(f'<span class="lt lts">{ps(s)}</span>' for s in ta["sup"][-4:])
        ress_html = "".join(f'<span class="lt ltr">{ps(r)}</span>' for r in ta["res"][-4:])
        if ta["at_bb_lo"]:   bb_s = "🟢 Lower band — mean reversion zone"
        elif ta["at_bb_up"]: bb_s = "🔴 Upper band — overextended"
        elif ta["bb_squeeze"]: bb_s = "🟡 Squeeze — breakout imminent"
        else:                bb_s = "⚪ Normal range"
        trend_c = "var(--teal)" if "Bull" in ta["trend"] else "var(--red)" if "Bear" in ta["trend"] else "var(--t2)"
        st.markdown(f"""
        <div style="font-size:.86rem;line-height:2.15;">
          <div>🔹 <strong>Trend:</strong> <span style="color:{trend_c}">{ta['trend']}</span></div>
          <div>🔹 <strong>Momentum:</strong> {ta['mom']}</div>
          <div>🔹 <strong>Volume:</strong> {'Above' if ta['vr']>1 else 'Below'} avg ({ta['vr']:.2f}×)</div>
          <div>🔹 <strong>VWAP:</strong> Price {'above' if ta['above_vwap'] else 'below'} ({ps(ta['vwap_v'])})</div>
          <div>🔹 <strong>Bollinger:</strong> {bb_s}</div>
          <div>🔹 <strong>Stochastic:</strong> K={ta['k_v']:.1f} / D={ta['d_v']:.1f}</div>
          <div>🔹 <strong>Liq. Sweep Low:</strong> {'🟢 YES (last 4 bars)' if ta['swept_lo'] else '⚪ No'}</div>
          <div>🔹 <strong>Liq. Sweep High:</strong> {'🔴 YES (last 4 bars)' if ta['swept_hi'] else '⚪ No'}</div>
          <div style="margin-top:.6rem;"><strong>Support levels:</strong><br>
            <div class="lr">{sups_html or '<span style="color:var(--t3);font-size:.7rem">None detected</span>'}</div>
          </div>
          <div style="margin-top:.4rem;"><strong>Resistance levels:</strong><br>
            <div class="lr">{ress_html or '<span style="color:var(--t3);font-size:.7rem">None detected</span>'}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Fibonacci
        st.markdown('<div class="card ca-gold">', unsafe_allow_html=True)
        st.markdown(f'<div class="ct">◈ FIBONACCI RETRACEMENT · 60D RANGE {ps(ta["fl"])} – {ps(ta["fh"])}</div>',
                    unsafe_allow_html=True)
        render_fib(ta["fibs"], p)
        st.markdown('</div>', unsafe_allow_html=True)

        # SMC
        st.markdown('<div class="card ca-purple">', unsafe_allow_html=True)
        st.markdown('<div class="ct">⬡ SMC: FVG + ORDER BLOCKS</div>', unsafe_allow_html=True)
        fb = [f for f in ta["fvgs"] if f["t"]=="bull"]
        fbe = [f for f in ta["fvgs"] if f["t"]=="bear"]
        ob = [o for o in ta["obs"] if o["t"]=="bull"]
        obe = [o for o in ta["obs"] if o["t"]=="bear"]
        inside_html = (
            '&nbsp;&nbsp;<strong style="color:var(--teal)">← PRICE INSIDE</strong>'
            if ta["in_bull_fvg"] else ""
        )
        bear_inside = (
            '&nbsp;&nbsp;<strong style="color:var(--red)">← PRICE INSIDE</strong>'
            if ta["in_bear_fvg"] else ""
        )
        ob_bull_html = (
            '&nbsp;&nbsp;<strong style="color:var(--teal)">← AT OB ZONE</strong>'
            if ta["at_bull_ob"] else ""
        )
        ob_bear_html = (
            '&nbsp;&nbsp;<strong style="color:var(--red)">← AT OB ZONE</strong>'
            if ta["at_bear_ob"] else ""
        )
        st.markdown(f"""
        <div style="font-size:.82rem;line-height:2.3;font-family:'Space Mono',monospace;">
          <div>Bull FVGs: <span style="color:var(--teal)">{len(fb)}</span>{inside_html}</div>
          <div>Bear FVGs: <span style="color:var(--red)">{len(fbe)}</span>{bear_inside}</div>
          <div>Bull OBs:  <span style="color:var(--teal)">{len(ob)}</span>{ob_bull_html}</div>
          <div>Bear OBs:  <span style="color:var(--red)">{len(obe)}</span>{ob_bear_html}</div>
        </div>""", unsafe_allow_html=True)
        if ta["fvgs"]:
            for f2 in reversed(ta["fvgs"][-3:]):
                fc = "var(--teal)" if f2["t"]=="bull" else "var(--red)"
                st.markdown(
                    f'<div style="font-family:Space Mono,monospace;font-size:.62rem;'
                    f'padding:.22rem 0;color:{fc};">'
                    f'{"BULL" if f2["t"]=="bull" else "BEAR"} FVG: '
                    f'{ps(f2["bot"])} – {ps(f2["top"])}</div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        # Strategy Votes
        st.markdown('<div class="card ca-gold">', unsafe_allow_html=True)
        st.markdown('<div class="ct">🎯 8-STRATEGY VOTE RESULTS</div>', unsafe_allow_html=True)
        render_strats(strats)
        st.markdown(f"""
        <div class="tb">
          <div class="ti tbuy"><div class="tn buy">{votes['BUY']}</div><div class="tl">BUY VOTES</div></div>
          <div class="ti tsell"><div class="tn sell">{votes['SELL']}</div><div class="tl">SELL VOTES</div></div>
          <div class="ti thold"><div class="tn hold">{votes['HOLD']}</div><div class="tl">HOLD VOTES</div></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # News
        st.markdown('<div class="card ca-teal">', unsafe_allow_html=True)
        sc = {"positive":"var(--teal)","negative":"var(--red)","neutral":"var(--t3)"}[sent_label]
        st.markdown(f"""
        <div class="ct">📰 NEWS SENTIMENT</div>
        <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.9rem;">
          <span style="font-family:'Bebas Neue',sans-serif;font-size:1.35rem;color:{sc};">{sent_label.upper()}</span>
          <span style="font-family:'Space Mono',monospace;font-size:.58rem;color:var(--t3);">AGGREGATE</span>
        </div>""", unsafe_allow_html=True)
        render_news(news)
        st.markdown('</div>', unsafe_allow_html=True)

        # Fundamentals
        st.markdown('<div class="card ca-teal">', unsafe_allow_html=True)
        st.markdown('<div class="ct">📊 FUNDAMENTALS</div>', unsafe_allow_html=True)
        if asset_type == "stock":
            rows_data = [
                ("Market Cap",     fmt(sg(meta,"marketCap"), "$")),
                ("P/E Ratio",      f'{sg(meta,"trailingPE"):.1f}' if sg(meta,"trailingPE") else "N/A"),
                ("EPS (TTM)",      f'${sg(meta,"trailingEps"):.2f}' if sg(meta,"trailingEps") else "N/A"),
                ("Revenue Growth", pct(sg(meta,"revenueGrowth"))),
                ("Gross Margin",   pct(sg(meta,"grossMargins"))),
                ("Debt/Equity",    f'{sg(meta,"debtToEquity"):.2f}' if sg(meta,"debtToEquity") else "N/A"),
                ("Free Cash Flow", fmt(sg(meta,"freeCashflow"), "$")),
                ("Dividend Yield", pct(sg(meta,"dividendYield"))),
                ("52W High",       ps(sg(meta,"fiftyTwoWeekHigh"))),
                ("52W Low",        ps(sg(meta,"fiftyTwoWeekLow"))),
                ("Beta",           f'{sg(meta,"beta"):.2f}' if sg(meta,"beta") else "N/A"),
                ("Sector",         sg(meta,"sector","N/A")),
            ]
        else:
            md = meta.get("market_data", {})
            rows_data = [
                ("Market Cap",   fmt(md.get("market_cap",{}).get("usd"), "$")),
                ("24h Volume",   fmt(md.get("total_volume",{}).get("usd"), "$")),
                ("Circ. Supply", fmt(md.get("circulating_supply"))),
                ("Max Supply",   fmt(md.get("max_supply")) if md.get("max_supply") else "∞ Unlimited"),
                ("All-Time High",ps(md.get("ath",{}).get("usd"))),
                ("ATH Change",   f'{md.get("ath_change_percentage",{}).get("usd",0):.1f}%'),
                ("24h Change",   f'{md.get("price_change_percentage_24h",0):+.2f}%'),
                ("7d Change",    f'{md.get("price_change_percentage_7d",0):+.2f}%'),
                ("30d Change",   f'{md.get("price_change_percentage_30d",0):+.2f}%'),
                ("CMC Rank",     f'#{meta.get("market_cap_rank","N/A")}'),
            ]
        fund_html = ""
        for lb, vl in rows_data:
            fund_html += (f'<div style="display:flex;justify-content:space-between;'
                          f'padding:.38rem 0;border-bottom:1px solid var(--border);">'
                          f'<span style="font-family:Space Mono,monospace;font-size:.65rem;color:var(--t3);">{lb}</span>'
                          f'<span style="font-family:Space Mono,monospace;font-size:.73rem;color:var(--t1);">{vl}</span>'
                          f'</div>')
        st.markdown(fund_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RECOMMENDATION ───────────────────────────────────
    divider("FINANCIAL RISK SUMMARY · TRADE RECOMMENDATION")

    rc1, rc2 = st.columns([2, 1], gap="medium")

    with rc1:
        rcls = {"BUY":"rbuy","SELL":"rsell","HOLD":"rhold"}[reco["dir"]]
        psl  = (reco["sl"]-p)/p*100
        ptp1 = (reco["tp1"]-p)/p*100
        ptp2 = (reco["tp2"]-p)/p*100
        paras_html = "".join(f'<p>{par}</p>' for par in reco["paras"])
        st.markdown(f"""
        <div class="rb {rcls}">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
            <div>
              <div class="rv" style="color:{dc};">{reco['dir']}</div>
              <div class="rtk">{ticker} · RISK: {reco['risk']} · SIZE: {reco['pos']}</div>
            </div>
            <div style="font-family:'Space Mono',monospace;text-align:right;">
              <div style="font-size:.56rem;color:var(--t3);margin-bottom:.4rem;">SL / TP1 / TP2</div>
              <div style="font-size:.8rem;color:var(--red);">{ps(reco['sl'])} ({psl:+.1f}%)</div>
              <div style="font-size:.8rem;color:var(--teal);">{ps(reco['tp1'])} ({ptp1:+.1f}%)</div>
              <div style="font-size:.8rem;color:var(--teal);">{ps(reco['tp2'])} ({ptp2:+.1f}%)</div>
              <div style="font-size:.72rem;color:var(--gold);margin-top:.4rem;">R/R  1:{reco['rr']:.1f}</div>
            </div>
          </div>
          <hr style="border:none;border-top:1px solid var(--border);margin:.9rem 0;">
          <div class="rbody">{paras_html}</div>
        </div>""", unsafe_allow_html=True)

    with rc2:
        YOUR_WR = 68.0
        pc2 = "var(--teal)" if wp_val >= YOUR_WR else "var(--gold)" if wp_val >= 58 else "var(--red)"
        edge = wp_val - YOUR_WR
        ec = "var(--teal)" if edge >= 0 else "var(--red)"
        st.markdown(f"""
        <div class="card ca-gold" style="text-align:center;padding:2rem 1.2rem;">
          <div class="ct" style="justify-content:center;">◈ WIN PROBABILITY</div>
          <div class="wpn" style="color:{pc2};">{wp_val:.1f}%</div>
          <div class="wpl">ATLAS multi-strategy estimate</div>
          <hr style="border:none;border-top:1px solid var(--border);margin:1.1rem 0;">
          <div style="font-family:'Space Mono',monospace;font-size:.62rem;color:var(--t3);">YOUR BASELINE</div>
          <div style="font-family:'Space Mono',monospace;font-size:1.45rem;font-weight:700;color:var(--t1);">{YOUR_WR:.0f}%</div>
          <div style="font-family:'Space Mono',monospace;font-size:.8rem;color:{ec};margin-top:.3rem;">
            {'EDGE +' if edge>=0 else 'EDGE '}{edge:.1f}%
          </div>
          <hr style="border:none;border-top:1px solid var(--border);margin:1.1rem 0;">
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;color:var(--t3);">CONFIDENCE</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:2.3rem;color:var(--gold);">{reco['conf']}/10</div>
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;color:var(--t3);margin-top:.5rem;">STRATEGIES USED</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.9rem;color:var(--t2);">8 / 8</div>
        </div>""", unsafe_allow_html=True)

        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=wp_val,
            number={"suffix":"%","font":{"family":"Space Mono","color":"#eef0f4","size":18}},
            gauge={
                "axis":{"range":[0,100],"tickfont":{"size":8,"family":"Space Mono"}},
                "bar":{"color":"#00d4aa" if wp_val>=YOUR_WR else "#c9a84c" if wp_val>=58 else "#ff4d6d","thickness":0.22},
                "bgcolor":"#0e1118","borderwidth":1,"bordercolor":"rgba(255,255,255,0.06)",
                "steps":[
                    {"range":[0,50],"color":"rgba(255,77,109,0.07)"},
                    {"range":[50,68],"color":"rgba(201,168,76,0.07)"},
                    {"range":[68,100],"color":"rgba(0,212,170,0.07)"},
                ],
                "threshold":{"line":{"color":"#c9a84c","width":2},"thickness":0.75,"value":YOUR_WR}
            }
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono"), height=185,
            margin=dict(l=15, r=15, t=8, b=8)
        )
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

    # ── FOOTER ───────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;margin-top:3rem;padding:1.2rem;border-top:1px solid var(--border);
        font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.15em;color:var(--t3);">
      ATLAS v4.0 · {ticker} · {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} ·
      DATA: YAHOO FINANCE + COINGECKO · 8 STRATEGIES · NOT FINANCIAL ADVICE
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────
elif not query:
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 0 2rem;">
      <div style="font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.25em;
          color:var(--t3);margin-bottom:2.5rem;">
        TYPE ANY NAME OR SYMBOL ABOVE · SEARCH SUGGESTIONS APPEAR AUTOMATICALLY
      </div>
      <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:3rem;">
    """, unsafe_allow_html=True)

    examples = [
        ("AAPL","Apple","STOCK"),("NVDA","Nvidia","STOCK"),("TSLA","Tesla","STOCK"),
        ("MSFT","Microsoft","STOCK"),("AMZN","Amazon","STOCK"),("META","Meta","STOCK"),
        ("BTC","Bitcoin","CRYPTO"),("ETH","Ethereum","CRYPTO"),("SOL","Solana","CRYPTO"),
        ("BNB","BNB","CRYPTO"),("XRP","Ripple","CRYPTO"),("DOGE","Dogecoin","CRYPTO"),
    ]
    items = ""
    for sym, name, typ in examples:
        color = "var(--teal)" if typ=="CRYPTO" else "var(--gold)"
        items += (f'<div style="text-align:center;">'
                  f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.65rem;'
                  f'letter-spacing:.08em;color:{color};">{sym}</div>'
                  f'<div style="font-family:\'Space Mono\',monospace;font-size:.55rem;'
                  f'color:var(--t3);">{name}</div></div>')

    st.markdown(items + """
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.16em;
          color:var(--t3);line-height:3.2;text-align:center;">
        ⬡ PELOSI-LIQUIDITY CONFLUENCE &nbsp;·&nbsp; EMA CROSSOVER + RSI &nbsp;·&nbsp; LIQUIDITY SWEEP + ORDER BLOCK<br>
        ⬡ MACD DIVERGENCE &nbsp;·&nbsp; VOLUME + FIBONACCI &nbsp;·&nbsp; BOLLINGER BAND BREAKOUT<br>
        ⬡ VWAP + STOCHASTIC &nbsp;·&nbsp; EMA STACK TREND STRENGTH<br>
        ⬡ REAL DATA · LIVE NEWS · STOP LOSS + TP LEVELS · WIN PROBABILITY VS YOUR 68%
      </div>
    </div>""", unsafe_allow_html=True)
