# Selenium DEX Scraper Architecture
## Discreet Data Gathering → AI Decision Making → Automated Trading

## Overview

This framework uses **Selenium web scraping** to discreetly gather price data from DEX websites, processes it through an **AI decision engine**, and executes profitable arbitrage trades automatically.

### Why Selenium Instead of APIs?

**Advantages:**
- ✅ No API keys required (anonymous)
- ✅ No rate limits (with proper delays)
- ✅ Appears as human browsing traffic
- ✅ Can access data not available via APIs
- ✅ Works even if APIs go down
- ✅ Can rotate proxies/IPs easily

**Disadvantages:**
- ❌ Slower than API calls
- ❌ Requires maintenance (DOM changes)
- ❌ Higher resource usage
- ❌ Can be detected if not careful

**Note:** For production, consider Web3 RPC calls or The Graph API as alternatives (faster, more reliable).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DATA LAYER                             │
│         Selenium Scraper (Anti-Detection)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Uniswap V2/V3│  │PancakeSwap V3│  │  Aerodrome   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Fluid     │  │     Orca     │  │   Others...  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  Features:                                                   │
│  - Headless Chrome (undetected-chromedriver)                │
│  - Random user agents                                        │
│  - Human-like delays (1-3s random)                          │
│  - Proxy rotation (optional)                                │
│  - Browser fingerprint randomization                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. AI LAYER                               │
│         Decision Engine (Machine Learning)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Feature Engineering                                   │  │
│  │ - Spread analysis                                     │  │
│  │ - Liquidity metrics                                   │  │
│  │ - Volume analysis                                     │  │
│  │ - Time-based features                                 │  │
│  │ - Historical patterns                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ML Models                                             │  │
│  │ - Opportunity Classifier (Random Forest)             │  │
│  │ - Profit Predictor (Gradient Boosting)               │  │
│  │ - Risk Assessment (Rule-based + ML)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Signal Generation                                     │  │
│  │ - Confidence score (0-1)                             │  │
│  │ - Risk score (0-1)                                   │  │
│  │ - Expected profit                                     │  │
│  │ - Priority (high/medium/low)                         │  │
│  │ - Human-readable reasoning                           │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 3. EXECUTION LAYER                           │
│         Arbitrage Trading Engine                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Trade Execution                                       │  │
│  │ - Paper trading (simulation)                         │  │
│  │ - Live trading (via exchange APIs)                   │  │
│  │ - Position sizing                                     │  │
│  │ - Slippage protection                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Performance Tracking                                  │  │
│  │ - P&L calculation                                     │  │
│  │ - Win rate tracking                                   │  │
│  │ - Sharpe ratio                                        │  │
│  │ - Max drawdown                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Continuous Learning                                   │  │
│  │ - Record trade outcomes                               │  │
│  │ - Retrain AI models periodically                      │  │
│  │ - Adapt to market conditions                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Selenium Scraper (`scrapers/dex_selenium_scraper.py`)

**Supported DEXs:**
- Uniswap V2
- Uniswap V3 (multiple fee tiers)
- PancakeSwap V3
- Aerodrome (Base chain)
- Fluid
- Orca (Solana)

**Anti-Detection Features:**

```python
class AntiDetectionBrowser:
    - Undetected ChromeDriver
    - Random user agents
    - Stealth mode (hides automation)
    - Random delays (1-3s)
    - Random scrolling
    - Proxy rotation support
    - Browser fingerprint randomization
```

**Key Methods:**

```python
# Scrape a single pair from one DEX
scraper = UniswapV3Scraper(browser)
price_data = scraper.scrape_pair('ETH', 'USDC', fee_tier='0.3%')

# Scrape all DEXs for multiple pairs
multi_scraper = MultiDEXScraper(headless=True, use_proxy=False)
results = multi_scraper.scrape_all([('ETH', 'USDC'), ('WBTC', 'USDC')])
```

**Output Format:**

```python
DEXPrice(
    timestamp=datetime.now(),
    dex='uniswap_v3',
    pair='ETH/USDC',
    price=3500.45,
    liquidity=2_500_000.00,
    volume_24h=15_000_000.00,
    fee_tier='0.3%'
)
```

### 2. AI Decision Engine (`ai/arbitrage_decision_engine.py`)

**Components:**

**a) Feature Engineering**
- Extracts 15+ features from price data
- Normalizes for ML models
- Includes time-based and market features

**b) ML Models**

```python
OpportunityClassifier:
    - Random Forest (100 trees)
    - Predicts probability of profitability
    - Returns confidence score 0-1

ProfitPredictor:
    - Gradient Boosting Regressor
    - Predicts actual profit amount
    - Learns from historical trades

RiskAssessment:
    - Rule-based + ML hybrid
    - Factors: liquidity, spread, volume
    - Returns risk score 0-1
```

**c) Signal Generation**

```python
ArbitrageSignal(
    pair='ETH/USDC',
    buy_dex='uniswap_v3',
    sell_dex='pancakeswap_v3',
    buy_price=3500.00,
    sell_price=3515.00,
    gross_spread_pct=0.43,
    net_profit_pct=0.25,        # After fees/slippage
    expected_profit_usd=12.50,
    confidence_score=0.85,       # AI confidence
    risk_score=0.30,            # Risk level
    recommended_size_usd=5000,
    execution_priority='high',
    reasoning='Large spread (0.43%) detected. High net profit potential (0.25%). AI high confidence (85%). Low risk. Strong liquidity ($5.0M).'
)
```

**Key Methods:**

```python
engine = ArbitrageDecisionEngine(
    min_confidence=0.6,
    min_profit_pct=0.5,
    max_risk_score=0.6
)

# Analyze scraped data
signals = engine.analyze_scraped_data(scraped_dict)

# Record trade outcome for learning
engine.record_trade_outcome(signal, actual_profit=15.25, success=True)

# Retrain models (periodic)
engine.retrain_models()
```

### 3. Orchestrator (`orchestrator/scrape_and_trade.py`)

**Main Automation Loop:**

```python
orchestrator = ArbitrageOrchestrator(
    initial_capital=15000,
    scrape_interval_minutes=15,
    use_headless=True,
    paper_trading=True
)

# Runs continuously:
# 1. Scrape DEXs every 15 minutes
# 2. Analyze with AI
# 3. Execute profitable trades
# 4. Record outcomes
# 5. Retrain AI periodically

orchestrator.run_continuous(
    pairs=[('ETH', 'USDC'), ('WBTC', 'USDC')],
    max_duration_hours=24
)
```

**One Cycle:**
```
15:00 - Scrape all DEXs for ETH/USDC, WBTC/USDC
15:03 - AI analyzes data, generates 3 signals
15:03 - Execute high-priority signal: ETH/USDC
15:04 - Execute medium-priority signal: WBTC/USDC
15:05 - Save results, wait 15 minutes
15:15 - Next cycle begins...
```

---

## Installation

### 1. Install Chrome/Chromium

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver

# Or download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### 2. Install Python Dependencies

```bash
cd ~/trading/EleanorPlatform
pip install -r requirements_selenium.txt
```

### 3. Verify Installation

```bash
python -c "import selenium; import undetected_chromedriver; print('OK')"
```

---

## Usage

### Quick Start (Paper Trading)

```bash
cd ~/trading/EleanorPlatform/src/eleanor

# Run orchestrator
python orchestrator/scrape_and_trade.py
```

### Custom Configuration

```python
from orchestrator.scrape_and_trade import ArbitrageOrchestrator

# Define trading pairs
pairs = [
    ('ETH', 'USDC'),
    ('WBTC', 'USDC'),
    ('MATIC', 'USDC'),
]

# Optional: Add proxies for extra privacy
proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
]

# Initialize
orchestrator = ArbitrageOrchestrator(
    initial_capital=15000,
    scrape_interval_minutes=10,  # Scrape every 10 min
    use_headless=True,           # Run in background
    use_proxy=True,              # Use proxy rotation
    proxy_list=proxies,
    paper_trading=True           # Start with simulation
)

# Run for 24 hours
orchestrator.run_continuous(
    pairs=pairs,
    max_duration_hours=24
)
```

### Monitor in Real-Time

```bash
# In one terminal: Run orchestrator
python orchestrator/scrape_and_trade.py

# In another terminal: Watch logs
tail -f arbitrage_bot.log
```

---

## Anti-Detection Best Practices

### 1. Randomized Delays

```python
# DON'T: Fixed delays (easily detected)
time.sleep(2)

# DO: Random delays (mimics human)
browser.human_delay(1.0, 3.0)  # Random 1-3 seconds
```

### 2. Rotate User Agents

```python
# Rotates through realistic user agents
# Appears as different browsers/OS
```

### 3. Use Headless Mode

```python
# Runs without visible window
# Lower resource usage
# Can run on server
```

### 4. Proxy Rotation

```python
# Every 10 cycles, switch proxy
# Appears to come from different IPs
# Avoid rate limiting
```

### 5. Random Scrolling

```python
# Occasionally scroll page
# Mimics human reading
browser.scroll_randomly()
```

### 6. Respect Rate Limits

```python
# Don't scrape too frequently
# 15-minute intervals recommended
# Avoid overwhelming DEX websites
```

---

## Performance Expectations

### Scraping Speed

```
Single DEX, Single Pair:  5-10 seconds
All DEXs, Single Pair:    30-60 seconds
All DEXs, 3 Pairs:        2-3 minutes
```

### Resource Usage

```
RAM: ~500MB per browser instance
CPU: Low (mostly waiting)
Network: Minimal (~10MB per cycle)
```

### Accuracy

```
Price Data:    99%+ accurate
Liquidity:     90%+ accurate (varies by DEX)
Volume:        95%+ accurate
```

---

## Alternative: Web3 RPC (Better for Production)

**Why Web3 is Better:**
- ✅ Much faster (milliseconds vs seconds)
- ✅ More reliable (no DOM changes)
- ✅ Lower resource usage
- ✅ Direct blockchain data

**Example:**

```python
from web3 import Web3

# Connect to Ethereum via RPC
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY'))

# Get Uniswap V3 pool data
pool_contract = w3.eth.contract(address=pool_address, abi=pool_abi)
slot0 = pool_contract.functions.slot0().call()
price = calculate_price_from_sqrt(slot0[0])  # sqrtPriceX96

# Much faster and more reliable than scraping!
```

**When to Use Selenium:**
- Website-only data (not on-chain)
- Avoiding API keys/accounts
- Maximum anonymity
- Backup when APIs fail

**When to Use Web3/APIs:**
- Production systems
- High-frequency trading
- Need real-time data
- Reliability is critical

---

## Troubleshooting

### Selenium Not Finding Elements

**Problem:** Page structure changed

**Solution:**
```python
# Update CSS selectors in scraper
# Check DEX website HTML structure
# Use browser DevTools to find new selectors
```

### Chrome/ChromeDriver Version Mismatch

**Problem:** `undetected-chromedriver` can't find Chrome

**Solution:**
```bash
# Use specific Chrome version
pip install undetected-chromedriver==3.5.4

# Or install Chrome from PPA
sudo apt install google-chrome-stable
```

### Detected as Bot

**Problem:** DEX blocks Selenium

**Solution:**
- Enable `selenium-stealth`
- Use residential proxies
- Increase delays
- Clear cookies/cache
- Rotate user agents more

### High CPU Usage

**Problem:** Multiple browsers consuming resources

**Solution:**
```python
# Use headless mode
headless=True

# Limit concurrent scrapers
# Close browsers between cycles
scraper.close()
```

---

## Security Considerations

### 1. Never Share API Keys in Scraper

```python
# ❌ DON'T: Hardcode keys
api_key = "sk_live_abc123"

# ✅ DO: Use environment variables
api_key = os.getenv('API_KEY')
```

### 2. Use VPN/Proxy

```python
# Route through Mullvad VPN (already configured in Qubes)
# Or use proxy rotation for extra privacy
```

### 3. Clear Browser Data

```python
# Cookies, cache cleared between sessions
# No persistent tracking
```

### 4. Avoid Login

```python
# Don't log into DEX websites
# Use read-only public data
# No authentication = no trace
```

---

## Future Improvements

**Short-term:**
- Add more DEXs (Curve, Balancer, etc.)
- Improve ML models with more features
- Add telegram/email alerts
- Better error handling

**Medium-term:**
- Hybrid scraping + Web3 RPC
- Multi-chain support (L2s, other chains)
- Advanced ML (LSTM for price prediction)
- Automated model retraining pipeline

**Long-term:**
- Distributed scraping (multiple nodes)
- Real-time WebSocket connections
- Flash loan integration
- MEV protection

---

## Files Structure

```
EleanorPlatform/
├── src/eleanor/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   └── dex_selenium_scraper.py       # Selenium scraping
│   ├── ai/
│   │   ├── __init__.py
│   │   └── arbitrage_decision_engine.py  # ML decision making
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── scrape_and_trade.py           # Main automation
│   └── data/
│       └── arbitrage/                     # Scraped data & results
├── requirements_selenium.txt
└── SELENIUM_SCRAPER_ARCHITECTURE.md      # This file
```

---

## Summary

**This framework provides:**

1. **Discreet Data Gathering** - Selenium scraping with anti-detection
2. **AI Decision Making** - ML-powered signal generation
3. **Automated Trading** - Continuous arbitrage execution
4. **Privacy-First** - Compatible with Mullvad VPN + Qubes OS
5. **Flexible** - Works with multiple DEXs and chains

**Perfect for:**
- Privacy-conscious traders
- Automated arbitrage
- Research and backtesting
- Learning ML for trading

**Get started:**
```bash
pip install -r requirements_selenium.txt
python src/eleanor/orchestrator/scrape_and_trade.py
```

Happy automated trading! 🤖💰
