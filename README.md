# ATLAS — Quantitative Trading Intelligence
## Setup & Run Guide

---

### REQUIREMENTS
- Python 3.9 or higher
- pip (Python package manager)
- Internet connection (fetches live market data)

---

### QUICK START (3 steps)

**Step 1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2 — Run the app**
```bash
streamlit run app.py
```

**Step 3 — Open in browser**
Your browser will open automatically at:
```
http://localhost:8501
```

---

### OPTIONAL: FREE NEWS API KEY (Finnhub)

For enhanced news headlines, get a FREE Finnhub key:
1. Go to https://finnhub.io → Sign Up (free)
2. Copy your API key from the dashboard
3. Set it as an environment variable before running:

**Mac/Linux:**
```bash
export FINNHUB_API_KEY=your_key_here
streamlit run app.py
```

**Windows:**
```cmd
set FINNHUB_API_KEY=your_key_here
streamlit run app.py
```

Without the key, the app still works — it uses Yahoo Finance RSS feeds and CryptoCompare news as fallback (both free, no key needed).

---

### SUPPORTED TICKERS

**Stocks (via Yahoo Finance — any valid ticker):**
- US Stocks: AAPL, NVDA, TSLA, MSFT, AMZN, META, GOOGL, JPM, etc.
- ETFs: SPY, QQQ, VTI, etc.
- International: Any Yahoo Finance ticker (e.g., BABA, TSM)

**Crypto (via CoinGecko — use these symbols):**
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, MATIC, LTC, LINK, UNI, ATOM, SHIB, PEPE, ARB, OP, NEAR, APT

---

### WHAT THE APP DOES

**Data Sources (all free, no key required):**
- Yahoo Finance → stock OHLCV, fundamentals, info
- CoinGecko → crypto OHLCV, market data, supply info
- Yahoo Finance RSS → news headlines (free)
- CryptoCompare → crypto news (free)
- Finnhub → enhanced news (optional free API key)

**Technical Analysis:**
- EMA 50 & EMA 200 with crossover detection
- RSI (14) with overbought/oversold zones
- MACD line, signal, and histogram
- Fibonacci retracement (0.236, 0.382, 0.5, 0.618, 0.786)
- Liquidity zones (pivot-based support/resistance)
- Fair Value Gap (FVG) detection (bullish + bearish)
- Order Block detection (bullish + bearish)
- Break of Structure (BOS) detection
- Volume analysis (20-period average ratio)

**5 Strategy Engine:**
1. Pelosi-Liquidity Confluence (liquidity sweep + FVG + EMA alignment)
2. EMA Crossover + RSI
3. Liquidity Sweep + Order Block
4. MACD Divergence
5. Volume + Fibonacci

**Final Output:**
- Vote tally (BUY / SELL / HOLD per strategy)
- Win probability estimate (calibrated to beat your 68% baseline)
- Specific stop loss, TP1, TP2 levels
- Risk classification + position sizing
- Confidence score /10

---

### TROUBLESHOOTING

**"No data found" error:**
- Check ticker spelling (use uppercase: AAPL not aapl)
- For crypto, use the symbol from the supported list above
- Some tickers may not have 6 months of data (new listings)

**Slow load:**
- First load may take 10-15 seconds (fetching 6 months OHLCV + news)
- Subsequent searches are cached for 5 minutes

**CoinGecko rate limit:**
- Free tier: 30 calls/min. If you get a 429 error, wait 60 seconds and retry.

---

### DISCLAIMER
This tool is for educational and informational purposes only.
Nothing in ATLAS constitutes financial advice.
Always do your own research before making investment decisions.
Past win rates do not guarantee future results.
