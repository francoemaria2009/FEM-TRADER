import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import warnings
import os
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATLAS — Quantitative Trading Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — DARK LUXURY FINANCIAL DESIGN
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=Bebas+Neue&display=swap');

:root {
  --bg-primary: #08090d;
  --bg-secondary: #0e1118;
  --bg-card: #111520;
  --bg-card-hover: #161b2a;
  --border: rgba(255,255,255,0.06);
  --border-accent: rgba(0,212,170,0.3);
  --gold: #c9a84c;
  --gold-light: #e5c878;
  --teal: #00d4aa;
  --teal-dim: rgba(0,212,170,0.12);
  --red: #ff4d6d;
  --red-dim: rgba(255,77,109,0.12);
  --blue: #4d9fff;
  --text-primary: #eef0f4;
  --text-secondary: #8892a4;
  --text-muted: #4a5568;
  --font-display: 'Bebas Neue', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'Space Mono', monospace;
}

html, body, [class*="css"] {
  font-family: var(--font-body);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.stApp {
  background: var(--bg-primary);
}

/* Hide streamlit default elements */
#MainMenu, footer, .stDeployButton, header { display: none !important; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1400px !important; }

/* ── HEADER ── */
.atlas-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 1.4rem 0 1.2rem;
  margin: 0 -2rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.atlas-header::before {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.atlas-logo {
  font-family: var(--font-display);
  font-size: 3.2rem;
  letter-spacing: 0.18em;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 0.2rem;
}
.atlas-logo span { color: var(--gold); }
.atlas-sub {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* ── SEARCH ── */
.search-wrap {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
}
.search-wrap::after {
  content: '';
  position: absolute;
  bottom: 0; left: 10%; right: 10%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-light), transparent);
  opacity: 0.3;
}
.stTextInput > div > div > input {
  background: #060810 !important;
  border: 1px solid rgba(201,168,76,0.25) !important;
  border-radius: 3px !important;
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
  font-size: 1.1rem !important;
  letter-spacing: 0.1em !important;
  padding: 0.85rem 1.2rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 1px rgba(201,168,76,0.2) !important;
}
.stButton > button {
  background: linear-gradient(135deg, #c9a84c, #a07830) !important;
  border: none !important;
  border-radius: 3px !important;
  color: #08090d !important;
  font-family: var(--font-display) !important;
  font-size: 1.2rem !important;
  letter-spacing: 0.12em !important;
  padding: 0.72rem 2.2rem !important;
  width: 100% !important;
  transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── CARDS ── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}
.card-accent-teal { border-left: 2px solid var(--teal); }
.card-accent-gold { border-left: 2px solid var(--gold); }
.card-accent-red  { border-left: 2px solid var(--red); }
.card-title {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.5rem;
}

/* ── METRIC TILES ── */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.metric-tile {
  background: #0b0e17;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 1.1rem 1.2rem;
}
.metric-label {
  font-family: var(--font-mono);
  font-size: 0.55rem;
  letter-spacing: 0.18em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}
.metric-value {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}
.metric-change { font-size: 0.75rem; margin-top: 0.2rem; }
.up { color: var(--teal); } .down { color: var(--red); }

/* ── STRATEGY VOTES ── */
.strategy-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--border);
}
.strategy-row:last-child { border-bottom: none; }
.strategy-name {
  font-family: var(--font-body);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  flex: 1;
}
.strategy-detail {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  flex: 2; padding: 0 1rem;
}
.vote-badge {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  font-weight: 700;
  padding: 0.3rem 0.9rem;
  border-radius: 2px;
  min-width: 70px;
  text-align: center;
}
.vote-buy  { background: rgba(0,212,170,0.15); color: var(--teal); border: 1px solid rgba(0,212,170,0.3); }
.vote-sell { background: rgba(255,77,109,0.15); color: var(--red);  border: 1px solid rgba(255,77,109,0.3); }
.vote-hold { background: rgba(77,159,255,0.1);  color: var(--blue); border: 1px solid rgba(77,159,255,0.25); }

/* ── VOTE TALLY ── */
.tally-bar {
  display: flex; gap: 0.5rem; margin: 1.2rem 0;
  font-family: var(--font-mono);
}
.tally-item {
  flex: 1; padding: 1rem; border-radius: 3px; text-align: center;
}
.tally-num { font-size: 2rem; font-weight: 700; line-height: 1; }
.tally-lbl { font-size: 0.6rem; letter-spacing: 0.15em; margin-top: 0.3rem; color: rgba(255,255,255,0.5); }
.tally-buy  { background: rgba(0,212,170,0.12); border: 1px solid rgba(0,212,170,0.25); }
.tally-sell { background: rgba(255,77,109,0.12); border: 1px solid rgba(255,77,109,0.25); }
.tally-hold { background: rgba(77,159,255,0.08); border: 1px solid rgba(77,159,255,0.2); }
.tally-num.buy  { color: var(--teal); }
.tally-num.sell { color: var(--red); }
.tally-num.hold { color: var(--blue); }

/* ── RECOMMENDATION BOX ── */
.reco-box {
  border-radius: 4px;
  padding: 1.8rem 2rem;
  margin-top: 1rem;
  border-width: 1px;
  border-style: solid;
}
.reco-buy  { background: rgba(0,212,170,0.06); border-color: rgba(0,212,170,0.35); }
.reco-sell { background: rgba(255,77,109,0.06); border-color: rgba(255,77,109,0.35); }
.reco-hold { background: rgba(77,159,255,0.05); border-color: rgba(77,159,255,0.3); }
.reco-verdict {
  font-family: var(--font-display);
  font-size: 2.8rem;
  letter-spacing: 0.08em;
  line-height: 1;
  margin-bottom: 0.3rem;
}
.reco-ticker {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  margin-bottom: 1.2rem;
}
.reco-body {
  font-family: var(--font-body);
  font-size: 0.92rem;
  line-height: 1.7;
  color: var(--text-secondary);
}
.reco-body strong { color: var(--text-primary); font-weight: 600; }

/* ── WIN PROBABILITY ── */
.win-prob-wrap {
  text-align: center; padding: 1.5rem 0;
}
.win-prob-num {
  font-family: var(--font-display);
  font-size: 4.5rem;
  letter-spacing: 0.05em;
  line-height: 1;
}
.win-prob-lbl {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: 0.3rem;
}

/* ── NEWS ── */
.news-item {
  display: flex; align-items: flex-start; gap: 0.9rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--border);
}
.news-item:last-child { border-bottom: none; }
.news-dot {
  width: 7px; height: 7px; border-radius: 50%; margin-top: 0.4rem; flex-shrink: 0;
}
.news-pos  { background: var(--teal); }
.news-neg  { background: var(--red); }
.news-neut { background: var(--text-muted); }
.news-headline {
  font-size: 0.88rem; color: var(--text-secondary); line-height: 1.45;
  flex: 1;
}
.news-sent {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  padding: 0.2rem 0.5rem;
  border-radius: 2px;
  flex-shrink: 0; margin-top: 0.15rem;
}
.sent-pos  { background: rgba(0,212,170,0.12); color: var(--teal); }
.sent-neg  { background: rgba(255,77,109,0.12); color: var(--red); }
.sent-neut { background: rgba(74,85,104,0.3); color: var(--text-muted); }

/* ── TECHNICAL LEVEL TAGS ── */
.level-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.4rem 0; }
.level-tag {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  padding: 0.25rem 0.6rem;
  border-radius: 2px;
  border: 1px solid var(--border);
  color: var(--text-muted);
}
.level-support { border-color: rgba(0,212,170,0.3); color: var(--teal); }
.level-resist  { border-color: rgba(255,77,109,0.3); color: var(--red); }
.level-fib     { border-color: rgba(201,168,76,0.3); color: var(--gold); }

/* ── SECTION DIVIDER ── */
.section-divider {
  display: flex; align-items: center; gap: 1rem; margin: 1.8rem 0 1.2rem;
}
.section-divider-line { flex: 1; height: 1px; background: var(--border); }
.section-divider-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  text-transform: uppercase;
  white-space: nowrap;
}

/* ── SPINNER OVERRIDE ── */
.stSpinner > div { border-top-color: var(--gold) !important; }
.stProgress .st-bo { background: var(--gold) !important; }

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background: #060810 !important;
  border-color: rgba(201,168,76,0.2) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
}

/* ── WARNINGS / INFO ── */
.stAlert { border-radius: 3px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="atlas-header">
  <div class="atlas-logo">AT<span>L</span>AS</div>
  <div class="atlas-sub">Quantitative Trading Intelligence · v2.0 · Multi-Strategy Engine</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPER — FORMAT NUMBERS
# ─────────────────────────────────────────────────────────────
def fmt_num(n, prefix="", suffix="", decimals=2):
    if n is None or (isinstance(n, float) and np.isnan(n)):
        return "N/A"
    try:
        n = float(n)
        if abs(n) >= 1e12: return f"{prefix}{n/1e12:.{decimals}f}T{suffix}"
        if abs(n) >= 1e9:  return f"{prefix}{n/1e9:.{decimals}f}B{suffix}"
        if abs(n) >= 1e6:  return f"{prefix}{n/1e6:.{decimals}f}M{suffix}"
        if abs(n) >= 1e3:  return f"{prefix}{n/1e3:.{decimals}f}K{suffix}"
        return f"{prefix}{n:.{decimals}f}{suffix}"
    except: return "N/A"

def pct_fmt(n):
    if n is None or (isinstance(n, float) and np.isnan(n)): return "N/A"
    try: return f"{float(n)*100:+.2f}%"
    except: return "N/A"

def safe_get(obj, key, default=None):
    try:
        v = obj.get(key, default)
        if v is None or (isinstance(v, float) and np.isnan(v)): return default
        return v
    except: return default

# ─────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────
CRYPTO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana", "XRP": "ripple", "ADA": "cardano",
    "DOGE": "dogecoin", "AVAX": "avalanche-2", "DOT": "polkadot",
    "MATIC": "matic-network", "LTC": "litecoin", "LINK": "chainlink",
    "UNI": "uniswap", "ATOM": "cosmos", "XLM": "stellar",
    "ALGO": "algorand", "FIL": "filecoin", "NEAR": "near",
    "APT": "aptos", "ARB": "arbitrum", "OP": "optimism",
    "TRUMP": "maga", "PEPE": "pepe", "SHIB": "shiba-inu",
}

def detect_asset_type(ticker: str) -> str:
    t = ticker.upper().strip()
    if t in CRYPTO_IDS: return "crypto"
    # Try to detect by fetching yfinance
    try:
        info = yf.Ticker(t).info
        if info.get("quoteType") in ("CRYPTOCURRENCY", "CURRENCY"): return "crypto"
        if info.get("regularMarketPrice") or info.get("currentPrice"): return "stock"
    except: pass
    return "stock"

@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str, period="6mo"):
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period=period, interval="1d")
        if df.empty: return None, {}
        info = tk.info or {}
        return df, info
    except Exception as e:
        return None, {}

@st.cache_data(ttl=300)
def fetch_crypto_ohlcv(coin_id: str, days=180):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return None
        data = r.json()
        df = pd.DataFrame(data, columns=["timestamp","Open","High","Low","Close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df["Volume"] = 0
        # Get volume from market_chart
        url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
        r2 = requests.get(url2, timeout=15)
        if r2.status_code == 200:
            vdata = r2.json().get("total_volumes", [])
            if vdata:
                vdf = pd.DataFrame(vdata, columns=["ts","Volume"])
                vdf["ts"] = pd.to_datetime(vdf["ts"], unit="ms").dt.normalize()
                vdf.set_index("ts", inplace=True)
                df.index = df.index.normalize()
                df["Volume"] = vdf["Volume"].reindex(df.index).fillna(0)
        return df
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_crypto_info(coin_id: str):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return {}
        return r.json()
    except: return {}

@st.cache_data(ttl=600)
def fetch_news(ticker: str, asset_type: str):
    """Try multiple free news sources"""
    headlines = []
    
    # Source 1: Finnhub free (no key for general news)
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Finnhub company news (free, no key for basic)
        finnhub_key = os.environ.get("FINNHUB_API_KEY", "")
        if finnhub_key:
            url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={week_ago}&to={today}&token={finnhub_key}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for item in data[:8]:
                    headlines.append(item.get("headline", ""))
    except: pass

    # Source 2: Yahoo Finance RSS (always free)
    if len(headlines) < 5:
        try:
            import xml.etree.ElementTree as ET
            q = ticker if asset_type == "stock" else ticker
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={q}&region=US&lang=en-US"
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for item in root.findall(".//item")[:10]:
                    title = item.findtext("title")
                    if title: headlines.append(title)
        except: pass

    # Source 3: GNews free (no key)
    if len(headlines) < 5:
        try:
            query = ticker
            url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max=5&apikey=free"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                for art in r.json().get("articles", []):
                    headlines.append(art.get("title",""))
        except: pass

    # Source 4: CryptoCompare news for crypto
    if asset_type == "crypto" and len(headlines) < 5:
        try:
            url = f"https://min-api.cryptocompare.com/data/v2/news/?categories={ticker}&excludeCategories=Sponsored"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for art in r.json().get("Data", [])[:8]:
                    headlines.append(art.get("title",""))
        except: pass

    return list(dict.fromkeys([h for h in headlines if h]))[:10]

# ─────────────────────────────────────────────────────────────
# TECHNICAL ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────
def compute_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, adjust=False).mean()
    avg_loss = loss.ewm(com=period-1, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def compute_fibonacci(high, low):
    diff = high - low
    levels = {
        "0.0 (High)": high,
        "0.236": high - 0.236 * diff,
        "0.382": high - 0.382 * diff,
        "0.500": high - 0.500 * diff,
        "0.618": high - 0.618 * diff,
        "0.786": high - 0.786 * diff,
        "1.0 (Low)": low,
    }
    return levels

def detect_pivot_highs_lows(high_series, low_series, window=5):
    pivot_highs, pivot_lows = [], []
    for i in range(window, len(high_series) - window):
        h = high_series.iloc[i]
        l = low_series.iloc[i]
        if h == max(high_series.iloc[i-window:i+window+1]):
            pivot_highs.append((high_series.index[i], h))
        if l == min(low_series.iloc[i-window:i+window+1]):
            pivot_lows.append((low_series.index[i], l))
    return pivot_highs, pivot_lows

def detect_fvg(df):
    """Fair Value Gaps: gaps between candle 1 high and candle 3 low (bullish FVG)"""
    fvgs = []
    for i in range(2, len(df)):
        # Bullish FVG: candle i-2 high < candle i low
        if df["Low"].iloc[i] > df["High"].iloc[i-2]:
            fvgs.append({
                "type": "bullish", "index": i,
                "top": df["Low"].iloc[i],
                "bottom": df["High"].iloc[i-2],
                "date": df.index[i]
            })
        # Bearish FVG: candle i-2 low > candle i high
        elif df["High"].iloc[i] < df["Low"].iloc[i-2]:
            fvgs.append({
                "type": "bearish", "index": i,
                "top": df["Low"].iloc[i-2],
                "bottom": df["High"].iloc[i],
                "date": df.index[i]
            })
    return fvgs[-10:] if len(fvgs) > 10 else fvgs  # return recent ones

def detect_order_blocks(df):
    """Order Blocks: last bearish candle before bullish impulse (and vice versa)"""
    obs = []
    for i in range(3, len(df)-2):
        # Bullish OB: bearish candle followed by strong bullish move
        if (df["Close"].iloc[i] < df["Open"].iloc[i] and
            df["Close"].iloc[i+1] > df["Open"].iloc[i+1] and
            df["Close"].iloc[i+1] > df["High"].iloc[i]):
            obs.append({
                "type": "bullish", "index": i,
                "top": df["High"].iloc[i],
                "bottom": df["Low"].iloc[i],
                "date": df.index[i]
            })
        # Bearish OB: bullish candle followed by strong bearish move
        elif (df["Close"].iloc[i] > df["Open"].iloc[i] and
              df["Close"].iloc[i+1] < df["Open"].iloc[i+1] and
              df["Close"].iloc[i+1] < df["Low"].iloc[i]):
            obs.append({
                "type": "bearish", "index": i,
                "top": df["High"].iloc[i],
                "bottom": df["Low"].iloc[i],
                "date": df.index[i]
            })
    return obs[-10:] if len(obs) > 10 else obs

def detect_bos(df, pivot_highs, pivot_lows):
    """Break of Structure"""
    bos_signals = []
    current_close = df["Close"].iloc[-1]
    # Check if recent close breaks above recent pivot high (bullish BOS)
    if pivot_highs:
        recent_ph = pivot_highs[-1][1]
        if current_close > recent_ph:
            bos_signals.append({"type": "bullish", "level": recent_ph})
    # Check if recent close breaks below recent pivot low (bearish BOS)
    if pivot_lows:
        recent_pl = pivot_lows[-1][1]
        if current_close < recent_pl:
            bos_signals.append({"type": "bearish", "level": recent_pl})
    return bos_signals

def run_technical_analysis(df):
    """Run all TA and return results dict"""
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]
    vol   = df["Volume"]

    ta = {}
    ta["ema50"]   = compute_ema(close, 50)
    ta["ema200"]  = compute_ema(close, 200)
    ta["rsi"]     = compute_rsi(close)
    macd_line, signal_line, hist = compute_macd(close)
    ta["macd_line"]   = macd_line
    ta["signal_line"] = signal_line
    ta["macd_hist"]   = hist
    ta["vol_ma20"]    = vol.rolling(20).mean()

    # Current values
    ta["current_price"] = float(close.iloc[-1])
    ta["current_ema50"]  = float(ta["ema50"].iloc[-1])
    ta["current_ema200"] = float(ta["ema200"].iloc[-1])
    ta["current_rsi"]    = float(ta["rsi"].iloc[-1])
    ta["current_macd"]   = float(macd_line.iloc[-1])
    ta["current_signal"] = float(signal_line.iloc[-1])
    ta["current_hist"]   = float(hist.iloc[-1])
    ta["current_vol"]    = float(vol.iloc[-1])
    ta["avg_vol_20"]     = float(ta["vol_ma20"].iloc[-1]) if not np.isnan(ta["vol_ma20"].iloc[-1]) else 1
    ta["vol_ratio"]      = ta["current_vol"] / ta["avg_vol_20"] if ta["avg_vol_20"] > 0 else 1

    # Fibonacci (last 60 days)
    lookback = min(60, len(df))
    ta["fib_high"] = float(high.iloc[-lookback:].max())
    ta["fib_low"]  = float(low.iloc[-lookback:].min())
    ta["fib_levels"] = compute_fibonacci(ta["fib_high"], ta["fib_low"])

    # Pivots
    ta["pivot_highs"], ta["pivot_lows"] = detect_pivot_highs_lows(high, low)

    # Liquidity zones
    ta["liquidity_support"] = sorted([p[1] for p in ta["pivot_lows"][-4:]])
    ta["liquidity_resistance"] = sorted([p[1] for p in ta["pivot_highs"][-4:]], reverse=True)

    # FVG & OB
    ta["fvgs"] = detect_fvg(df)
    ta["order_blocks"] = detect_order_blocks(df)
    ta["bos"] = detect_bos(df, ta["pivot_highs"], ta["pivot_lows"])

    # Trend
    p = ta["current_price"]
    e50 = ta["current_ema50"]
    e200 = ta["current_ema200"]
    if p > e50 > e200:     ta["trend"] = "Bullish"
    elif p < e50 < e200:   ta["trend"] = "Bearish"
    elif p > e200:         ta["trend"] = "Neutral-Bullish"
    else:                  ta["trend"] = "Neutral-Bearish"

    # Momentum
    ta["momentum"] = "Strong" if abs(ta["current_rsi"] - 50) > 15 else "Weak"

    # Support / Resistance nearest
    sup = [x for x in ta["liquidity_support"] if x < p]
    res = [x for x in ta["liquidity_resistance"] if x > p]
    ta["nearest_support"]    = max(sup) if sup else ta["fib_low"]
    ta["nearest_resistance"] = min(res) if res else ta["fib_high"]

    # 20-day range
    ta["high_20"] = float(high.iloc[-20:].max())
    ta["low_20"]  = float(low.iloc[-20:].min())

    # EMA Crossover (recent)
    ema50_arr  = ta["ema50"].values
    ema200_arr = ta["ema200"].values
    ta["ema_golden_cross"] = (ema50_arr[-2] <= ema200_arr[-2] and ema50_arr[-1] > ema200_arr[-1])
    ta["ema_death_cross"]  = (ema50_arr[-2] >= ema200_arr[-2] and ema50_arr[-1] < ema200_arr[-1])

    # MACD crossover
    macd_arr   = macd_line.values
    signal_arr = signal_line.values
    ta["macd_bull_cross"] = (macd_arr[-2] <= signal_arr[-2] and macd_arr[-1] > signal_arr[-1])
    ta["macd_bear_cross"] = (macd_arr[-2] >= signal_arr[-2] and macd_arr[-1] < signal_arr[-1])

    # Liquidity sweep detection: price swept 20-day high/low within last 5 candles
    recent_5 = df.iloc[-5:]
    ta["swept_high"] = any(recent_5["High"] >= ta["high_20"] * 0.999)
    ta["swept_low"]  = any(recent_5["Low"]  <= ta["low_20"]  * 1.001)

    # FVG proximity: is current price inside a recent FVG?
    ta["in_bull_fvg"] = any(f["type"]=="bullish" and f["bottom"] <= p <= f["top"] for f in ta["fvgs"])
    ta["in_bear_fvg"] = any(f["type"]=="bearish" and f["bottom"] <= p <= f["top"] for f in ta["fvgs"])

    # OB proximity
    ta["at_bull_ob"] = any(ob["type"]=="bullish" and ob["bottom"] <= p <= ob["top"] for ob in ta["order_blocks"])
    ta["at_bear_ob"] = any(ob["type"]=="bearish" and ob["bottom"] <= p <= ob["top"] for ob in ta["order_blocks"])

    # Divergence (last 20 bars)
    if len(df) >= 20:
        recent_close = close.iloc[-20:]
        recent_macd  = macd_line.iloc[-20:]
        ta["bull_div"] = (recent_close.iloc[-1] < recent_close.iloc[0] and recent_macd.iloc[-1] > recent_macd.iloc[0])
        ta["bear_div"] = (recent_close.iloc[-1] > recent_close.iloc[0] and recent_macd.iloc[-1] < recent_macd.iloc[0])
    else:
        ta["bull_div"] = ta["bear_div"] = False

    # Fibonacci proximity (within 1.5% of level)
    ta["at_fib_618"] = any(abs(p - v) / p < 0.015 for k, v in ta["fib_levels"].items() if "0.618" in k)
    ta["at_fib_786"] = any(abs(p - v) / p < 0.015 for k, v in ta["fib_levels"].items() if "0.786" in k)

    return ta

# ─────────────────────────────────────────────────────────────
# STRATEGY ENGINE
# ─────────────────────────────────────────────────────────────
def run_strategies(ta: dict, has_insider_signal=False):
    results = {}
    p   = ta["current_price"]
    rsi = ta["current_rsi"]
    e50 = ta["current_ema50"]
    e200= ta["current_ema200"]
    vr  = ta["vol_ratio"]

    # ── STRATEGY 1: Pelosi-Liquidity Confluence ──────────────
    s1_reasons = []
    if ta["swept_low"] and ta["in_bull_fvg"] and p > e50 > e200:
        s1_vote = "BUY"
        s1_reasons = ["Swept 20D low ✓", "Price in bullish FVG ✓", "EMA bullish stack ✓"]
    elif ta["swept_high"] and ta["in_bear_fvg"] and p < e50 < e200:
        s1_vote = "SELL"
        s1_reasons = ["Swept 20D high ✓", "Price in bearish FVG ✓", "EMA bearish stack ✓"]
    elif has_insider_signal and p > e50:
        s1_vote = "BUY"
        s1_reasons = ["Insider/unusual activity ✓", "Price above EMA50 ✓"]
    elif ta["swept_low"] and rsi < 45:
        s1_vote = "BUY"
        s1_reasons = ["Swept low ✓", "RSI < 45 ✓"]
    elif ta["swept_high"] and rsi > 55:
        s1_vote = "SELL"
        s1_reasons = ["Swept high ✓", "RSI > 55 ✓"]
    else:
        s1_vote = "HOLD"
        s1_reasons = ["No sweep+FVG confluence"]
    results["s1"] = {"vote": s1_vote, "name": "Pelosi-Liquidity Confluence", "detail": " | ".join(s1_reasons)}

    # ── STRATEGY 2: EMA Crossover + RSI ─────────────────────
    if (ta["ema_golden_cross"] or (p > e50 > e200 and e50 > e200 * 1.001)) and 30 <= rsi <= 70:
        s2_vote = "BUY"; s2_detail = f"EMA50>EMA200 | RSI {rsi:.1f} neutral zone"
    elif (ta["ema_death_cross"] or (p < e50 < e200 and e200 > e50 * 1.001)) and 30 <= rsi <= 70:
        s2_vote = "SELL"; s2_detail = f"EMA50<EMA200 | RSI {rsi:.1f} neutral zone"
    elif rsi > 70:
        s2_vote = "SELL"; s2_detail = f"RSI overbought {rsi:.1f} | Potential reversal"
    elif rsi < 30:
        s2_vote = "BUY"; s2_detail = f"RSI oversold {rsi:.1f} | Potential bounce"
    else:
        s2_vote = "HOLD"; s2_detail = f"No EMA crossover | RSI {rsi:.1f}"
    results["s2"] = {"vote": s2_vote, "name": "EMA Crossover + RSI", "detail": s2_detail}

    # ── STRATEGY 3: Liquidity Sweep + Order Block ────────────
    if ta["swept_low"] and ta["at_bull_ob"]:
        s3_vote = "BUY"; s3_detail = "Low swept ✓ | Bullish OB confirmed ✓"
    elif ta["swept_high"] and ta["at_bear_ob"]:
        s3_vote = "SELL"; s3_detail = "High swept ✓ | Bearish OB confirmed ✓"
    elif ta["swept_low"]:
        s3_vote = "BUY"; s3_detail = "Low swept ✓ | Awaiting OB reaction"
    elif ta["swept_high"]:
        s3_vote = "SELL"; s3_detail = "High swept ✓ | Awaiting OB reaction"
    elif ta["at_bull_ob"]:
        s3_vote = "BUY"; s3_detail = "Price at bullish Order Block"
    elif ta["at_bear_ob"]:
        s3_vote = "SELL"; s3_detail = "Price at bearish Order Block"
    else:
        s3_vote = "HOLD"; s3_detail = "No sweep/OB confluence active"
    results["s3"] = {"vote": s3_vote, "name": "Liquidity Sweep + Order Block", "detail": s3_detail}

    # ── STRATEGY 4: MACD Divergence ──────────────────────────
    if ta["bull_div"] or ta["macd_bull_cross"]:
        reason = "Bullish MACD divergence" if ta["bull_div"] else "MACD bullish crossover"
        s4_vote = "BUY"; s4_detail = f"{reason} | Hist: {ta['current_hist']:.4f}"
    elif ta["bear_div"] or ta["macd_bear_cross"]:
        reason = "Bearish MACD divergence" if ta["bear_div"] else "MACD bearish crossover"
        s4_vote = "SELL"; s4_detail = f"{reason} | Hist: {ta['current_hist']:.4f}"
    elif ta["current_hist"] > 0 and ta["current_macd"] > ta["current_signal"]:
        s4_vote = "BUY"; s4_detail = f"MACD bullish | Hist positive {ta['current_hist']:.4f}"
    elif ta["current_hist"] < 0 and ta["current_macd"] < ta["current_signal"]:
        s4_vote = "SELL"; s4_detail = f"MACD bearish | Hist negative {ta['current_hist']:.4f}"
    else:
        s4_vote = "HOLD"; s4_detail = "No MACD divergence signal"
    results["s4"] = {"vote": s4_vote, "name": "MACD Divergence Signal", "detail": s4_detail}

    # ── STRATEGY 5: Volume + Fibonacci ───────────────────────
    at_fib = ta["at_fib_618"] or ta["at_fib_786"]
    vol_up = vr > 1.3
    if at_fib and vol_up and rsi < 40:
        s5_vote = "BUY"; s5_detail = f"Fib 0.618/0.786 ✓ | Vol {vr:.1f}x avg | RSI {rsi:.1f}"
    elif at_fib and vol_up and rsi > 60:
        s5_vote = "SELL"; s5_detail = f"Fib 0.618/0.786 ✓ | Vol {vr:.1f}x avg | RSI {rsi:.1f}"
    elif vol_up and p > e50 and rsi < 50:
        s5_vote = "BUY"; s5_detail = f"High vol {vr:.1f}x | Above EMA50 | RSI {rsi:.1f}"
    elif vol_up and p < e50 and rsi > 55:
        s5_vote = "SELL"; s5_detail = f"High vol {vr:.1f}x | Below EMA50 | RSI {rsi:.1f}"
    else:
        s5_vote = "HOLD"; s5_detail = f"Vol {vr:.1f}x avg | Not at key Fib level"
    results["s5"] = {"vote": s5_vote, "name": "Volume + Fibonacci", "detail": s5_detail}

    return results

# ─────────────────────────────────────────────────────────────
# SENTIMENT ANALYSIS
# ─────────────────────────────────────────────────────────────
POSITIVE_WORDS = {"bullish","surge","rally","gain","profit","growth","record","beat","strong",
                  "upgrade","buy","outperform","positive","rise","soar","exceed","partnership","approve",
                  "launch","expansion","dividend","milestone","breakthrough","acquire","win"}
NEGATIVE_WORDS = {"bearish","crash","drop","decline","fall","loss","miss","downgrade","sell",
                  "underperform","negative","plunge","slump","investigation","lawsuit","recall","ban",
                  "default","bankruptcy","fraud","warning","cut","layoff","regulation","fine"}

def analyze_sentiment(headline: str):
    h = headline.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in h)
    neg = sum(1 for w in NEGATIVE_WORDS if w in h)
    if pos > neg: return "positive"
    if neg > pos: return "negative"
    return "neutral"

def overall_sentiment(headlines):
    if not headlines: return "neutral", "No recent news found"
    scores = [analyze_sentiment(h) for h in headlines]
    pos = scores.count("positive"); neg = scores.count("negative")
    if pos > neg * 1.2:   return "positive", headlines[0]
    if neg > pos * 1.2:   return "negative", headlines[0]
    return "neutral", headlines[0]

# ─────────────────────────────────────────────────────────────
# WIN PROBABILITY CALCULATOR
# ─────────────────────────────────────────────────────────────
def calculate_win_probability(strategy_results, ta, sentiment_label, votes):
    """Multi-factor win probability estimation"""
    buy_n  = votes["BUY"]
    sell_n = votes["SELL"]
    hold_n = votes["HOLD"]
    total_directional = buy_n + sell_n
    if total_directional == 0: return 50.0

    # Base: strategy agreement
    max_vote = max(buy_n, sell_n)
    agreement_pct = max_vote / 5  # 0..1

    # RSI factor
    rsi = ta["current_rsi"]
    p   = ta["current_price"]
    e50 = ta["current_ema50"]
    e200= ta["current_ema200"]

    rsi_factor = 0
    if (buy_n > sell_n and rsi < 65) or (sell_n > buy_n and rsi > 35): rsi_factor = 0.05
    if rsi < 30 or rsi > 70: rsi_factor += 0.03

    # EMA alignment factor
    ema_aligned = (buy_n > sell_n and p > e50 > e200) or (sell_n > buy_n and p < e50 < e200)
    ema_factor = 0.08 if ema_aligned else 0.0

    # Volume factor
    vol_factor = min(0.05, (ta["vol_ratio"] - 1) * 0.03) if ta["vol_ratio"] > 1 else 0

    # Sentiment factor
    sent_factor = 0.04 if sentiment_label == "positive" and buy_n > sell_n else \
                  0.04 if sentiment_label == "negative" and sell_n > buy_n else 0

    # FVG+OB factor
    fvg_ob_factor = 0.06 if (ta["in_bull_fvg"] and buy_n > sell_n) or (ta["in_bear_fvg"] and sell_n > buy_n) else 0

    base = 0.50 + agreement_pct * 0.25
    total = base + rsi_factor + ema_factor + vol_factor + sent_factor + fvg_ob_factor
    total = min(0.92, max(0.42, total))
    return round(total * 100, 1)

# ─────────────────────────────────────────────────────────────
# CHARTING
# ─────────────────────────────────────────────────────────────
def build_main_chart(df, ta, ticker):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.55, 0.22, 0.23],
        subplot_titles=[f"{ticker} Price Action", "Volume", "RSI / MACD"]
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#00d4aa", decreasing_line_color="#ff4d6d",
        increasing_fillcolor="rgba(0,212,170,0.6)", decreasing_fillcolor="rgba(255,77,109,0.6)",
        name="Price", showlegend=False
    ), row=1, col=1)

    # EMAs
    fig.add_trace(go.Scatter(
        x=df.index, y=ta["ema50"], name="EMA 50",
        line=dict(color="#c9a84c", width=1.5, dash="solid"), opacity=0.9
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=ta["ema200"], name="EMA 200",
        line=dict(color="#4d9fff", width=1.5, dash="dot"), opacity=0.9
    ), row=1, col=1)

    # Fibonacci levels (horizontal lines)
    for name, level in ta["fib_levels"].items():
        color = "#c9a84c" if "0.618" in name or "0.786" in name else "rgba(201,168,76,0.3)"
        fig.add_hline(y=level, line_dash="dash", line_color=color,
                      line_width=0.7, opacity=0.5, row=1, col=1,
                      annotation_text=name, annotation_position="right",
                      annotation_font_size=9, annotation_font_color=color)

    # Support / Resistance zones
    for sup in ta["liquidity_support"][-2:]:
        fig.add_hline(y=sup, line_dash="dot", line_color="rgba(0,212,170,0.4)",
                      line_width=0.8, row=1, col=1)
    for res in ta["liquidity_resistance"][-2:]:
        fig.add_hline(y=res, line_dash="dot", line_color="rgba(255,77,109,0.4)",
                      line_width=0.8, row=1, col=1)

    # Volume bars
    colors_vol = ["rgba(0,212,170,0.5)" if c >= o else "rgba(255,77,109,0.5)"
                  for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], marker_color=colors_vol, name="Volume", showlegend=False
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=ta["vol_ma20"], name="Vol MA20",
        line=dict(color="#c9a84c", width=1.2), opacity=0.8
    ), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=ta["rsi"], name="RSI 14",
        line=dict(color="#a78bfa", width=1.5)
    ), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,77,109,0.5)", line_width=0.8, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,212,170,0.5)", line_width=0.8, row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(167,139,250,0.04)", line_width=0, row=3, col=1)

    # MACD histogram overlay (secondary axis simulated with scaled values on RSI row — show on separate trace)
    fig.add_trace(go.Bar(
        x=df.index,
        y=ta["macd_hist"],
        name="MACD Hist",
        marker_color=["rgba(0,212,170,0.4)" if v >= 0 else "rgba(255,77,109,0.4)"
                      for v in ta["macd_hist"]],
        yaxis="y4",
        showlegend=True
    ), row=3, col=1)

    # Styling
    fig.update_layout(
        paper_bgcolor="#08090d",
        plot_bgcolor="#08090d",
        font=dict(family="Space Mono", color="#8892a4", size=10),
        legend=dict(
            bgcolor="rgba(14,17,24,0.9)", bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1, font=dict(size=10), x=0.01, y=0.99
        ),
        xaxis_rangeslider_visible=False,
        height=680,
        margin=dict(l=10, r=80, t=40, b=10),
    )
    for i in range(1, 4):
        fig.update_xaxes(
            gridcolor="rgba(255,255,255,0.04)", showgrid=True,
            zeroline=False, row=i, col=1,
            tickfont=dict(family="Space Mono", size=9)
        )
        fig.update_yaxes(
            gridcolor="rgba(255,255,255,0.04)", showgrid=True,
            zeroline=False, row=i, col=1,
            tickfont=dict(family="Space Mono", size=9),
            tickprefix="$" if i == 1 else ""
        )
    for ann in fig["layout"]["annotations"]:
        ann["font"]["family"] = "Space Mono"
        ann["font"]["size"] = 10
        ann["font"]["color"] = "#8892a4"

    return fig

# ─────────────────────────────────────────────────────────────
# RECOMMENDATION GENERATOR
# ─────────────────────────────────────────────────────────────
def generate_recommendation(ticker, ta, votes, strategy_results, sentiment_label, win_prob, asset_type):
    buy_n  = votes["BUY"]
    sell_n = votes["SELL"]
    hold_n = votes["HOLD"]
    p  = ta["current_price"]
    rsi = ta["current_rsi"]
    vr  = ta["vol_ratio"]

    direction = "BUY" if buy_n > sell_n else "SELL" if sell_n > buy_n else "HOLD"
    agreement = max(buy_n, sell_n, hold_n)

    # Risk level
    if agreement >= 4 and win_prob >= 72:  risk = "LOW-MEDIUM"
    elif agreement >= 3 and win_prob >= 65: risk = "MEDIUM"
    elif agreement >= 2:                    risk = "MEDIUM-HIGH"
    else:                                   risk = "HIGH"

    # Position size
    if risk == "LOW-MEDIUM":   pos_pct = "1.0–1.5%"
    elif risk == "MEDIUM":     pos_pct = "0.75–1.0%"
    elif risk == "MEDIUM-HIGH": pos_pct = "0.5%"
    else:                       pos_pct = "0.25–0.5%"

    # Stop loss / take profit
    atr_approx = float(ta.get("fib_high", p) - ta.get("fib_low", p)) / 60
    if direction == "BUY":
        sl  = ta["nearest_support"] * 0.995
        tp1 = p + (p - sl) * 1.5
        tp2 = ta["nearest_resistance"]
    elif direction == "SELL":
        sl  = ta["nearest_resistance"] * 1.005
        tp1 = p - (sl - p) * 1.5
        tp2 = ta["nearest_support"]
    else:
        sl  = ta["nearest_support"] * 0.99
        tp1 = ta["nearest_resistance"] * 0.995
        tp2 = ta["nearest_resistance"]

    # Confidence score
    conf = round(win_prob / 10, 1)

    # Narrative
    direction_word = "accumulate a long" if direction=="BUY" else "initiate a short" if direction=="SELL" else "stand aside on"
    sent_phrase = f"sentiment is {sentiment_label}, providing additional {'tailwind' if (direction=='BUY' and sentiment_label=='positive') or (direction=='SELL' and sentiment_label=='negative') else 'headwind'} context"

    p1 = (f"The multi-strategy engine returns **{buy_n} BUY, {sell_n} SELL, and {hold_n} HOLD** votes for {ticker}, "
          f"producing a clear {'majority' if agreement >= 3 else 'slim'} {direction} signal. "
          f"The {['Pelosi-Liquidity','EMA+RSI','Liquidity Sweep+OB','MACD','Volume+Fibonacci'][0]} strategy "
          f"{'confirms' if strategy_results['s1']['vote']==direction else 'abstains from'} this view. "
          f"Current news {sent_phrase}.")

    p2 = (f"Price is {'above' if p > ta['current_ema50'] else 'below'} EMA-50 "
          f"({'above' if p > ta['current_ema200'] else 'below'} EMA-200), "
          f"RSI at {rsi:.1f} ({'overbought' if rsi>70 else 'oversold' if rsi<30 else 'neutral'}), "
          f"and volume running at {vr:.1f}× the 20-period average. "
          f"Overall trend is classified as **{ta['trend']}** with **{ta['momentum']}** momentum. "
          f"Risk classification: **{risk}**. Recommended position: **{pos_pct} of portfolio**.")

    p3 = (f"Structural stop loss: **${sl:,.2f}** ({((sl-p)/p*100):+.2f}%). "
          f"First target: **${tp1:,.2f}** ({((tp1-p)/p*100):+.2f}%). "
          f"Extended target: **${tp2:,.2f}** ({((tp2-p)/p*100):+.2f}%). "
          f"This gives a minimum R/R of 1:{abs(tp1-p)/max(abs(p-sl),0.001):.1f}. "
          f"Confidence score: **{conf}/10**. "
          f"{'Invalidation: any 4H close below the swept low negates the bullish thesis.' if direction=='BUY' else 'Invalidation: any 4H close above the swept high negates the bearish thesis.' if direction=='SELL' else 'Wait for a decisive directional break before entering.'}")

    return {
        "direction": direction,
        "risk": risk,
        "pos_pct": pos_pct,
        "sl": sl, "tp1": tp1, "tp2": tp2,
        "conf": conf,
        "paragraphs": [p1, p2, p3]
    }

# ─────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────
def vote_badge_html(vote):
    cls = {"BUY":"vote-buy","SELL":"vote-sell","HOLD":"vote-hold"}.get(vote,"vote-hold")
    return f'<span class="vote-badge {cls}">{vote}</span>'

def render_strategy_table(strategy_results):
    rows_html = ""
    for k, s in strategy_results.items():
        badge = vote_badge_html(s["vote"])
        rows_html += f"""
        <div class="strategy-row">
          <div class="strategy-name">{s['name']}</div>
          <div class="strategy-detail">{s['detail']}</div>
          {badge}
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)

def render_news(headlines):
    if not headlines:
        st.markdown('<p style="color:var(--text-muted);font-size:0.85rem;">No headlines retrieved. Check API keys or try again.</p>', unsafe_allow_html=True)
        return
    items_html = ""
    for h in headlines[:10]:
        sent = analyze_sentiment(h)
        dot_cls  = {"positive":"news-pos","negative":"news-neg","neutral":"news-neut"}.get(sent)
        sent_cls = {"positive":"sent-pos","negative":"sent-neg","neutral":"sent-neut"}.get(sent)
        items_html += f"""
        <div class="news-item">
          <div class="news-dot {dot_cls}"></div>
          <div class="news-headline">{h}</div>
          <div class="news-sent {sent_cls}">{sent.upper()}</div>
        </div>"""
    st.markdown(items_html, unsafe_allow_html=True)

def render_fib_table(fib_levels, current_price):
    rows = ""
    for name, level in fib_levels.items():
        pct_from = (level - current_price) / current_price * 100
        is_key = "0.618" in name or "0.786" in name or "0.500" in name
        style = "color: var(--gold);" if is_key else ""
        rows += f"""
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.75rem;{style}">{name}</td>
          <td style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.8rem;">${level:,.4f}</td>
          <td style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.75rem;
              color:{'var(--teal)' if pct_from < 0 else 'var(--red)'};">{pct_from:+.2f}%</td>
        </tr>"""
    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr style="border-bottom:1px solid var(--border);">
        <th style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.6rem;
            letter-spacing:0.15em;color:var(--text-muted);text-align:left;">LEVEL</th>
        <th style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.6rem;
            letter-spacing:0.15em;color:var(--text-muted);text-align:left;">PRICE</th>
        <th style="padding:0.5rem 0.75rem;font-family:var(--font-mono);font-size:0.6rem;
            letter-spacing:0.15em;color:var(--text-muted);text-align:left;">FROM CURRENT</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="search-wrap">
  <p style="font-family:var(--font-mono);font-size:0.65rem;letter-spacing:0.2em;
     color:var(--text-muted);text-transform:uppercase;margin-bottom:0.75rem;">
     ◈ MULTI-STRATEGY ANALYSIS ENGINE · REAL-TIME DATA
  </p>
""", unsafe_allow_html=True)

col_input, col_btn = st.columns([3, 1])
with col_input:
    ticker_input = st.text_input(
        "", placeholder="Enter ticker symbol: AAPL · NVDA · BTC · ETH · TSLA · MSFT",
        label_visibility="collapsed"
    )
with col_btn:
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("⬡  ANALYZE", use_container_width=True)

st.markdown("""
  <p style="font-family:var(--font-mono);font-size:0.6rem;color:var(--text-muted);margin-top:0.75rem;">
    Stocks via Yahoo Finance · Crypto via CoinGecko · 5 institutional strategies · 100% real market data
  </p>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ANALYSIS EXECUTION
# ─────────────────────────────────────────────────────────────
if analyze_btn and ticker_input.strip():
    ticker = ticker_input.strip().upper()

    with st.spinner(f"Fetching live market data for {ticker}…"):
        asset_type = detect_asset_type(ticker)
        df = None
        info = {}
        crypto_info = {}

        if asset_type == "crypto":
            coin_id = CRYPTO_IDS.get(ticker, ticker.lower())
            df = fetch_crypto_ohlcv(coin_id, days=180)
            crypto_info = fetch_crypto_info(coin_id)
        else:
            df, info = fetch_stock_data(ticker, period="6mo")

    if df is None or df.empty:
        st.error(f"❌ Could not fetch data for **{ticker}**. Please verify the ticker symbol. For crypto, try symbols like BTC, ETH, SOL.")
        st.stop()

    if len(df) < 50:
        st.warning(f"⚠️ Only {len(df)} data points available. Some indicators may be less accurate.")

    with st.spinner("Running technical analysis + 5 strategies…"):
        ta = run_technical_analysis(df)
        headlines = fetch_news(ticker, asset_type)
        sent_label, top_headline = overall_sentiment(headlines)
        strategy_results = run_strategies(ta)

    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for s in strategy_results.values():
        votes[s["vote"]] += 1

    win_prob = calculate_win_probability(strategy_results, ta, sent_label, votes)
    reco = generate_recommendation(ticker, ta, votes, strategy_results, sent_label, win_prob, asset_type)

    p = ta["current_price"]

    # ── TICKER HEADER ──────────────────────────────────────
    change_pct = float(df["Close"].pct_change().iloc[-1]) * 100 if len(df) > 1 else 0
    change_sign = "up" if change_pct >= 0 else "down"
    direction_color = "var(--teal)" if reco["direction"]=="BUY" else "var(--red)" if reco["direction"]=="SELL" else "var(--blue)"

    st.markdown(f"""
    <div style="display:flex;align-items:flex-end;justify-content:space-between;
        padding:1.5rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem;">
      <div>
        <div style="font-family:var(--font-display);font-size:3.5rem;letter-spacing:0.05em;line-height:1;">
          {ticker}
        </div>
        <div style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.2em;
            color:var(--text-muted);text-transform:uppercase;margin-top:0.2rem;">
          {'CRYPTOCURRENCY' if asset_type=='crypto' else 'EQUITY'} · LIVE ANALYSIS
        </div>
      </div>
      <div style="text-align:right;">
        <div style="font-family:var(--font-mono);font-size:2.2rem;font-weight:700;line-height:1;">
          ${f"{p:,.4f}" if p < 1 else f"{p:,.2f}"}
        </div>
        <div class="{change_sign}" style="font-family:var(--font-mono);font-size:0.85rem;margin-top:0.2rem;">
          {change_pct:+.2f}% today
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRIC TILES ───────────────────────────────────────
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)

    def metric_tile(label, value, change_val=None, change_cls=None):
        change_html = f'<div class="metric-change {change_cls}">{change_val}</div>' if change_val else ""
        return f"""
        <div class="metric-tile">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          {change_html}
        </div>"""

    tiles = ""
    tiles += metric_tile("RSI (14)", f"{ta['current_rsi']:.1f}",
                          "Overbought" if ta['current_rsi']>70 else "Oversold" if ta['current_rsi']<30 else "Neutral",
                          "down" if ta['current_rsi']>70 else "up" if ta['current_rsi']<30 else None)
    tiles += metric_tile("EMA 50", f"${ta['current_ema50']:,.2f}",
                          "Bullish" if p > ta['current_ema50'] else "Bearish",
                          "up" if p > ta['current_ema50'] else "down")
    tiles += metric_tile("EMA 200", f"${ta['current_ema200']:,.2f}",
                          "Above" if p > ta['current_ema200'] else "Below",
                          "up" if p > ta['current_ema200'] else "down")
    tiles += metric_tile("Volume Ratio", f"{ta['vol_ratio']:.2f}×",
                          "High Volume" if ta['vol_ratio']>1.5 else "Normal",
                          "up" if ta['vol_ratio']>1.5 else None)
    tiles += metric_tile("MACD", f"{ta['current_macd']:.4f}",
                          "Bull" if ta['current_macd']>ta['current_signal'] else "Bear",
                          "up" if ta['current_macd']>ta['current_signal'] else "down")
    tiles += metric_tile("Trend", ta["trend"], ta["momentum"])

    if asset_type == "stock":
        mc = safe_get(info, "marketCap")
        pe = safe_get(info, "trailingPE")
        tiles += metric_tile("Market Cap", fmt_num(mc, "$"))
        tiles += metric_tile("P/E Ratio", f"{pe:.1f}" if pe else "N/A")
    else:
        mdata = crypto_info.get("market_data", {})
        mc = mdata.get("market_cap", {}).get("usd")
        vol24 = mdata.get("total_volume", {}).get("usd")
        tiles += metric_tile("Market Cap", fmt_num(mc, "$"))
        tiles += metric_tile("24h Volume", fmt_num(vol24, "$"))

    st.markdown(tiles + "</div>", unsafe_allow_html=True)

    # ── MAIN CHART ─────────────────────────────────────────
    st.markdown("""<div class="section-divider">
      <div class="section-divider-line"></div>
      <div class="section-divider-label">◈ PRICE ACTION · INDICATORS</div>
      <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)

    fig = build_main_chart(df, ta, ticker)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── LEFT / RIGHT COLUMNS ────────────────────────────────
    col_l, col_r = st.columns([1, 1], gap="medium")

    with col_l:
        # Technical Summary
        st.markdown('<div class="card card-accent-teal">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⬡ TECHNICAL SUMMARY</div>', unsafe_allow_html=True)
        supp_tags = "".join(f'<span class="level-tag level-support">${s:,.2f}</span>' for s in ta["liquidity_support"][-3:])
        res_tags  = "".join(f'<span class="level-tag level-resist">${r:,.2f}</span>' for r in ta["liquidity_resistance"][-3:])
        vol_text  = f"{'Above' if ta['vol_ratio']>1 else 'Below'} average ({ta['vol_ratio']:.2f}×)"
        st.markdown(f"""
        <div style="font-size:0.88rem;line-height:2;">
          <div>🔹 <strong>Trend:</strong> <span style="color:var(--{'teal' if 'Bull' in ta['trend'] else 'red' if 'Bear' in ta['trend'] else 'text-secondary'})">{ta['trend']}</span></div>
          <div>🔹 <strong>Momentum:</strong> {ta['momentum']}</div>
          <div>🔹 <strong>Volume:</strong> {vol_text}</div>
          <div>🔹 <strong>BOS Signal:</strong> {'🟢 Bullish BOS' if any(b['type']=='bullish' for b in ta['bos']) else '🔴 Bearish BOS' if any(b['type']=='bearish' for b in ta['bos']) else '⚪ No BOS'}</div>
          <div style="margin-top:0.5rem;"><strong>Support zones:</strong><br><div class="level-row">{supp_tags or '<span style="color:var(--text-muted)">No pivots detected</span>'}</div></div>
          <div style="margin-top:0.5rem;"><strong>Resistance zones:</strong><br><div class="level-row">{res_tags or '<span style="color:var(--text-muted)">No pivots detected</span>'}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Fibonacci
        st.markdown('<div class="card card-accent-gold">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">◈ FIBONACCI RETRACEMENT · 60-DAY RANGE</div>', unsafe_allow_html=True)
        render_fib_table(ta["fib_levels"], p)
        st.markdown('</div>', unsafe_allow_html=True)

        # FVG & OB Status
        st.markdown('<div class="card card-accent-gold">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⬡ SMC: FVG · ORDER BLOCKS</div>', unsafe_allow_html=True)
        fvg_bull = [f for f in ta["fvgs"] if f["type"]=="bullish"]
        fvg_bear = [f for f in ta["fvgs"] if f["type"]=="bearish"]
        ob_bull  = [o for o in ta["order_blocks"] if o["type"]=="bullish"]
        ob_bear  = [o for o in ta["order_blocks"] if o["type"]=="bearish"]
        st.markdown(f"""
        <div style="font-size:0.82rem;line-height:2.1;font-family:var(--font-mono);">
          <div>Bullish FVGs detected: <span style="color:var(--teal)">{len(fvg_bull)}</span>
            {'  ← <strong style="color:var(--teal)">PRICE INSIDE</strong>' if ta['in_bull_fvg'] else ''}</div>
          <div>Bearish FVGs detected: <span style="color:var(--red)">{len(fvg_bear)}</span>
            {'  ← <strong style="color:var(--red)">PRICE INSIDE</strong>' if ta['in_bear_fvg'] else ''}</div>
          <div>Bullish OBs detected: <span style="color:var(--teal)">{len(ob_bull)}</span>
            {'  ← <strong style="color:var(--teal)">PRICE AT OB</strong>' if ta['at_bull_ob'] else ''}</div>
          <div>Bearish OBs detected: <span style="color:var(--red)">{len(ob_bear)}</span>
            {'  ← <strong style="color:var(--red)">PRICE AT OB</strong>' if ta['at_bear_ob'] else ''}</div>
          <div>Liquidity sweep (low): <span style="color:{'var(--teal)' if ta['swept_low'] else 'var(--text-muted)'}">
            {'✓ YES' if ta['swept_low'] else '✗ NO'}</span></div>
          <div>Liquidity sweep (high): <span style="color:{'var(--red)' if ta['swept_high'] else 'var(--text-muted)'}">
            {'✓ YES' if ta['swept_high'] else '✗ NO'}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        # Strategy Votes
        st.markdown('<div class="card card-accent-gold">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 STRATEGY ENGINE · 5 SYSTEMS</div>', unsafe_allow_html=True)
        render_strategy_table(strategy_results)
        st.markdown(f"""
        <div class="tally-bar">
          <div class="tally-item tally-buy">
            <div class="tally-num buy">{votes['BUY']}</div>
            <div class="tally-lbl">BUY VOTES</div>
          </div>
          <div class="tally-item tally-sell">
            <div class="tally-num sell">{votes['SELL']}</div>
            <div class="tally-lbl">SELL VOTES</div>
          </div>
          <div class="tally-item tally-hold">
            <div class="tally-num hold">{votes['HOLD']}</div>
            <div class="tally-lbl">HOLD VOTES</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # News Sentiment
        st.markdown('<div class="card card-accent-teal">', unsafe_allow_html=True)
        sent_color = {"positive":"var(--teal)","negative":"var(--red)","neutral":"var(--text-muted)"}.get(sent_label)
        st.markdown(f"""
        <div class="card-title">📰 NEWS SENTIMENT</div>
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
          <span style="font-family:var(--font-display);font-size:1.4rem;letter-spacing:0.08em;color:{sent_color};">
            {sent_label.upper()}
          </span>
          <span style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted);">
            OVERALL SIGNAL
          </span>
        </div>
        """, unsafe_allow_html=True)
        render_news(headlines)
        st.markdown('</div>', unsafe_allow_html=True)

        # Fundamentals
        st.markdown('<div class="card card-accent-teal">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 FUNDAMENTALS</div>', unsafe_allow_html=True)
        if asset_type == "stock":
            eps = safe_get(info, "trailingEps"); pe = safe_get(info, "trailingPE")
            rev_growth = safe_get(info, "revenueGrowth"); de = safe_get(info, "debtToEquity")
            fcf = safe_get(info, "freeCashflow"); mc2 = safe_get(info, "marketCap")
            sector = safe_get(info, "sector", "N/A"); beta = safe_get(info, "beta")
            rows = [
                ("Market Cap",    fmt_num(mc2, "$")),
                ("P/E Ratio",     f"{pe:.1f}" if pe else "N/A"),
                ("EPS",           f"${eps:.2f}" if eps else "N/A"),
                ("Revenue Growth",pct_fmt(rev_growth)),
                ("Debt/Equity",   f"{de:.2f}" if de else "N/A"),
                ("Free Cash Flow",fmt_num(fcf, "$")),
                ("Sector",        str(sector)),
                ("Beta",          f"{beta:.2f}" if beta else "N/A"),
            ]
        else:
            mdata = crypto_info.get("market_data", {})
            mc2 = mdata.get("market_cap",{}).get("usd"); vol24h = mdata.get("total_volume",{}).get("usd")
            supply = mdata.get("circulating_supply"); max_s = mdata.get("max_supply")
            ch_24 = mdata.get("price_change_percentage_24h"); ch_7 = mdata.get("price_change_percentage_7d")
            ch_30 = mdata.get("price_change_percentage_30d")
            rank = crypto_info.get("market_cap_rank", "N/A")
            rows = [
                ("Market Cap",        fmt_num(mc2, "$")),
                ("24h Volume",        fmt_num(vol24h, "$")),
                ("Circulating Supply",fmt_num(supply)),
                ("Max Supply",        fmt_num(max_s) if max_s else "Unlimited"),
                ("24h Change",        f"{ch_24:+.2f}%" if ch_24 else "N/A"),
                ("7d Change",         f"{ch_7:+.2f}%" if ch_7 else "N/A"),
                ("30d Change",        f"{ch_30:+.2f}%" if ch_30 else "N/A"),
                ("CMC Rank",          f"#{rank}"),
            ]
        rows_html = ""
        for label, val in rows:
            rows_html += f"""
            <div style="display:flex;justify-content:space-between;padding:0.45rem 0;
                border-bottom:1px solid var(--border);">
              <span style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted);">{label}</span>
              <span style="font-family:var(--font-mono);font-size:0.78rem;color:var(--text-primary);">{val}</span>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── FINAL RECOMMENDATION ─────────────────────────────────
    st.markdown("""<div class="section-divider">
      <div class="section-divider-line"></div>
      <div class="section-divider-label">◈ RISK ASSESSMENT · RECOMMENDATION</div>
      <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)

    reco_col, prob_col = st.columns([2, 1], gap="medium")

    with reco_col:
        direction_color_map = {"BUY":"teal","SELL":"red","HOLD":"blue"}
        dc = direction_color_map.get(reco["direction"],"blue")
        reco_cls = {"BUY":"reco-buy","SELL":"reco-sell","HOLD":"reco-hold"}.get(reco["direction"],"reco-hold")
        body_html = "".join(f"<p>{p_}</p>" for p_ in reco["paragraphs"])
        body_html = body_html.replace("**","<strong>").replace("**","</strong>")
        # proper bold replace
        import re
        def bold_replace(text):
            return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        body_html_clean = "".join(f"<p style='margin-bottom:0.8rem;'>{bold_replace(pr)}</p>" for pr in reco["paragraphs"])

        st.markdown(f"""
        <div class="reco-box {reco_cls}">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
              <div class="reco-verdict" style="color:var(--{dc});">{reco['direction']}</div>
              <div class="reco-ticker">{ticker} · RISK: {reco['risk']} · POSITION: {reco['pos_pct']}</div>
            </div>
            <div style="text-align:right;font-family:var(--font-mono);">
              <div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:0.3rem;">SL / TP1 / TP2</div>
              <div style="font-size:0.8rem;color:var(--red);">${reco['sl']:,.2f}</div>
              <div style="font-size:0.8rem;color:var(--teal);">${reco['tp1']:,.2f}</div>
              <div style="font-size:0.8rem;color:var(--teal);">${reco['tp2']:,.2f}</div>
            </div>
          </div>
          <hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">
          <div class="reco-body">{body_html_clean}</div>
        </div>
        """, unsafe_allow_html=True)

    with prob_col:
        prob_color = "var(--teal)" if win_prob >= 68 else "var(--gold)" if win_prob >= 58 else "var(--red)"
        YOUR_WIN_RATE = 68
        edge = win_prob - YOUR_WIN_RATE
        edge_color = "var(--teal)" if edge >= 0 else "var(--red)"

        st.markdown(f"""
        <div class="card card-accent-gold" style="text-align:center;padding:2.5rem 1.5rem;">
          <div class="card-title" style="justify-content:center;">◈ ESTIMATED WIN PROBABILITY</div>
          <div class="win-prob-num" style="color:{prob_color};">{win_prob:.1f}%</div>
          <div class="win-prob-lbl">ATLAS confidence score</div>
          <hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0;">
          <div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-muted);">YOUR WIN RATE</div>
          <div style="font-family:var(--font-mono);font-size:1.5rem;font-weight:700;color:var(--text-primary);">
            {YOUR_WIN_RATE}%
          </div>
          <div style="margin-top:0.5rem;font-family:var(--font-mono);font-size:0.8rem;color:{edge_color};">
            {'EDGE: +' if edge >= 0 else 'EDGE: '}{edge:.1f}%
          </div>
          <hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0;">
          <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);">CONFIDENCE SCORE</div>
          <div style="font-family:var(--font-display);font-size:2.5rem;color:var(--gold);">{reco['conf']}/10</div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge chart
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=win_prob,
            domain={"x":[0,1],"y":[0,1]},
            title={"text":"", "font": {"size": 0}},
            number={"suffix":"%","font":{"family":"Space Mono","color":"#eef0f4","size":20}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#4a5568","tickfont":{"size":9,"family":"Space Mono"}},
                "bar":{"color": "#00d4aa" if win_prob>=68 else "#c9a84c" if win_prob>=58 else "#ff4d6d","thickness":0.25},
                "bgcolor":"#0e1118",
                "borderwidth":1,"bordercolor":"rgba(255,255,255,0.06)",
                "steps":[
                    {"range":[0,50],"color":"rgba(255,77,109,0.08)"},
                    {"range":[50,68],"color":"rgba(201,168,76,0.08)"},
                    {"range":[68,100],"color":"rgba(0,212,170,0.08)"},
                ],
                "threshold":{"line":{"color":"#c9a84c","width":2},"thickness":0.8,"value":YOUR_WIN_RATE}
            }
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono"),
            height=200, margin=dict(l=20,r=20,t=10,b=10)
        )
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

    # ── FOOTER ─────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;margin-top:3rem;padding:1.5rem;
        border-top:1px solid var(--border);
        font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.15em;color:var(--text-muted);">
      ATLAS QUANTITATIVE INTELLIGENCE · {ticker} ANALYSIS COMPLETED {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} ·
      DATA: YAHOO FINANCE + COINGECKO · NOT FINANCIAL ADVICE
    </div>
    """, unsafe_allow_html=True)

elif analyze_btn and not ticker_input.strip():
    st.warning("⚠️ Please enter a ticker symbol first.")
else:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:4rem 0 2rem;">
      <div style="font-family:var(--font-display);font-size:1.2rem;letter-spacing:0.25em;
          color:var(--text-muted);margin-bottom:2rem;">
        ENTER A TICKER ABOVE TO BEGIN
      </div>
      <div style="display:flex;justify-content:center;gap:3rem;flex-wrap:wrap;">
    """, unsafe_allow_html=True)

    examples = [
        ("AAPL", "Apple Inc", "STOCK"),
        ("NVDA", "Nvidia Corp", "STOCK"),
        ("TSLA", "Tesla Inc", "STOCK"),
        ("BTC", "Bitcoin", "CRYPTO"),
        ("ETH", "Ethereum", "CRYPTO"),
        ("SOL", "Solana", "CRYPTO"),
    ]
    items = ""
    for sym, name, typ in examples:
        color = "var(--teal)" if typ=="CRYPTO" else "var(--gold)"
        items += f"""
        <div style="text-align:center;cursor:pointer;">
          <div style="font-family:var(--font-display);font-size:1.8rem;
              letter-spacing:0.08em;color:{color};">{sym}</div>
          <div style="font-family:var(--font-mono);font-size:0.6rem;
              color:var(--text-muted);letter-spacing:0.12em;">{name}</div>
          <div style="font-family:var(--font-mono);font-size:0.55rem;
              color:var(--text-muted);opacity:0.5;">{typ}</div>
        </div>"""

    st.markdown(items + """
      </div>
      <div style="margin-top:4rem;font-family:var(--font-mono);font-size:0.62rem;
          letter-spacing:0.18em;color:var(--text-muted);line-height:2.5;">
        <div>⬡ PELOSI-LIQUIDITY CONFLUENCE STRATEGY</div>
        <div>⬡ EMA CROSSOVER + RSI SIGNAL</div>
        <div>⬡ LIQUIDITY SWEEP + ORDER BLOCK</div>
        <div>⬡ MACD DIVERGENCE DETECTION</div>
        <div>⬡ VOLUME + FIBONACCI ANALYSIS</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
