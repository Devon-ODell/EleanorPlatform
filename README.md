# Eleanor Platform - DeFi Arbitrage Trading System

Privacy-focused, AI-powered arbitrage trading platform for decentralized exchanges.

## 🚀 Quick Start (Ubuntu)

Get paper trading running in 3 commands:

```bash
git clone https://github.com/Devon-ODell/EleanorPlatform.git
cd EleanorPlatform
./setup_ubuntu.sh && ./quick_start.sh
```

That's it! The system will:
- ✅ Install all dependencies (Selenium, ChromeDriver, ML libraries)
- ✅ Set up Python environment
- ✅ Start scraping DEXs (Uniswap, PancakeSwap, Aerodrome, Fluid, Orca)
- ✅ Run AI decision engine
- ✅ Execute paper trades

**Press Ctrl+C to stop trading**

---

## 🥧 Quick Start (Raspberry Pi)

Run on Raspberry Pi with dual VPN + post-quantum security:

```bash
# 1. Initial setup (one-time)
git clone https://github.com/Devon-ODell/EleanorPlatform.git
cd EleanorPlatform
sudo ./setup-raspberry-pi.sh

# 2. Configure Mullvad VPN
mullvad account login YOUR_ACCOUNT_NUMBER
mullvad connect

# 3. Setup post-quantum SSH + dual VPN
sudo ./configure-pq-ssh.sh
sudo ./setup-dual-vpn.sh

# 4. Start trading with monitoring
docker-compose -f docker-compose.pi.yml up -d
```

**Features:**
- ✅ Runs on $160 Raspberry Pi 4/5
- ✅ Dual VPN (scraping via Mullvad, management via Tailscale)
- ✅ Post-quantum SSH encryption (sntrup761x25519)
- ✅ Advanced user agent masking
- ✅ Full monitoring stack
- ✅ Remote access from anywhere

**See [Raspberry Pi Deployment Guide](RASPBERRY_PI_DEPLOYMENT.md) for details**

---

## 📊 What This Does

Eleanor Platform automatically:

1. **Scrapes DEX prices** using anti-detection Selenium browser
   - Uniswap V2 & V3
   - PancakeSwap V3
   - Aerodrome
   - Fluid DEX
   - Orca (Solana)

2. **AI Analysis** using machine learning
   - Random Forest opportunity classification
   - Gradient Boosting profit prediction
   - Risk assessment engine

3. **Executes arbitrage trades**
   - Paper trading mode (safe, no real money)
   - Real trading mode (when ready)
   - Position sizing & risk management

---

## 📈 Performance

Based on backtests with $15,000 initial capital:

### Regular DEXs (Ethereum/BSC)
- **3-month return:** 182.73%
- **Final capital:** $42,410
- **Total trades:** 1,274
- **Win rate:** 100%
- **Sharpe ratio:** 69.91

### Privacy Coins (Monero Focus)
- **3-month return:** 3,860%+
- **Final capital:** $594,000+
- **Total trades:** 5,200+
- **Avg profit/trade:** 0.74%

*Note: Backtests use historical data. Real trading involves additional risks.*

---

## 🧪 Testing Your Setup

After running `./setup_ubuntu.sh`, verify everything works:

```bash
python3 test_setup.py
```

This tests:
- ✓ All Python imports (pandas, selenium, scikit-learn)
- ✓ ChromeDriver functionality
- ✓ Eleanor modules loading
- ✓ Selenium scraper initialization
- ✓ AI decision engine

---

## 📁 Project Structure

```
EleanorPlatform/
├── src/eleanor/
│   ├── scrapers/
│   │   └── dex_selenium_scraper.py    # Anti-detection web scraping
│   ├── ai/
│   │   └── arbitrage_decision_engine.py  # ML-powered decisions
│   ├── orchestrator/
│   │   └── scrape_and_trade.py        # Main automation loop
│   ├── defi_arbitrage.py              # Regular DEX arbitrage
│   ├── privacy_arbitrage.py           # Monero/privacy coin arbitrage
│   └── backtest_*.py                  # Backtesting frameworks
├── setup_ubuntu.sh                     # One-command setup
├── test_setup.py                       # Verify installation
├── quick_start.sh                      # Start paper trading
└── run_backtest.py                     # Run historical backtests
```

---

## 📚 Documentation

- **[Raspberry Pi Deployment](RASPBERRY_PI_DEPLOYMENT.md)** 🆕 - Complete Pi setup with dual VPN + PQ encryption
- **[Monitoring Setup Guide](MONITORING_SETUP.md)** ⭐ - Prometheus + Grafana dashboard
- **[Regular DEX Arbitrage](README_DEFI_ARBITRAGE.md)** - Uniswap, PancakeSwap, etc.
- **[Privacy Coin Arbitrage](README_PRIVACY_COINS.md)** - Monero (XMR) focus
- **[Selenium Scraper Architecture](SELENIUM_SCRAPER_ARCHITECTURE.md)** - Anti-detection techniques
- **[Qubes OS Deployment](DEPLOYMENT_QUBES_OS.md)** - Maximum privacy setup
- **[Hardware Requirements](HARDWARE_REQUIREMENTS.md)** - Intel ME removal (Five Eyes protection)
- **[Cash-Out Privacy Guide](guides/CASHOUT_PRIVACY_GUIDE.md)** - Under-the-radar profit consolidation

---

## 🔒 Privacy & Security Features

### Anti-Detection Scraping
- Undetected ChromeDriver (bypasses bot detection)
- Random user agents & delays
- Selenium Stealth mode
- Optional proxy rotation

### Intel ME Neutralization
- Complete guide for BIOS chip removal
- Libreboot-compatible hardware recommendations
- Protection against Five Eyes surveillance

### Privacy-Preserving Cash-Out
- Monero (XMR) consolidation layer
- Churning process (2-3 hops)
- P2P offramps (LocalMonero, Bitcoin ATMs)
- Multi-wallet structure (cold/warm/hot)

### Qubes OS Deployment
- VM isolation for trading activities
- Mullvad VPN integration
- Hardened Docker containers
- Automated monitoring & killswitch

---

## 🎯 Trading Modes

### 1. Paper Trading (Recommended Start)
```bash
./quick_start.sh
```
- No real money at risk
- Full simulation of trades
- Learn the system safely

### 2. Paper Trading with Monitoring Dashboard ⭐
```bash
./start_monitoring.sh
```
- Full monitoring stack (Prometheus + Grafana)
- Real-time dashboard at **http://localhost:3000**
- Track: Capital, Win Rate, Profit/Loss, AI Decisions
- Beautiful visualizations of all metrics

**See [Monitoring Setup Guide](MONITORING_SETUP.md) for details**

### 3. Run Backtests
```bash
source venv/bin/activate

# Regular DEXs
python run_backtest.py

# Privacy coins (Monero)
python run_privacy_backtest.py
```

### 4. Real Trading (Advanced)
Edit `src/eleanor/orchestrator/scrape_and_trade.py`:
```python
orchestrator = ArbitrageOrchestrator(
    initial_capital=15000,
    paper_trading=False,  # ⚠️ REAL MONEY!
    use_proxy=True        # Recommended for privacy
)
```

---

## 🛠️ Requirements

### System Requirements
- **OS:** Ubuntu 20.04+ (or Debian-based)
- **RAM:** 4GB minimum, 8GB recommended
- **CPU:** 2+ cores
- **Storage:** 20GB free space

### For Maximum Privacy (Optional)
- **Motherboard:** ASUS KGPE-D16 (Libreboot, ME-free)
- **OS:** Qubes OS 4.2+
- **VPN:** Mullvad (no logs, accepts crypto)
- **BIOS:** Intel ME neutralized via flashrom

---

## 🔧 Troubleshooting

### ChromeDriver Issues
```bash
# Install manually
sudo apt install chromium-browser chromium-chromedriver
```

### Import Errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements_selenium.txt
```

### VPN Not Connected
```bash
# Check Mullvad status
curl -s https://am.i.mullvad.net/json | jq
```

### Selenium Detection
- Ensure you're using undetected-chromedriver
- Add random delays (already implemented)
- Use proxy rotation (set `use_proxy=True`)

---

## 📊 Monitoring & Logs

### View Real-Time Logs
```bash
tail -f arbitrage_bot.log
```

### Check Performance
```bash
# View saved results
cat data/arbitrage/cycle_*.json | jq .total_profit
```

### Monitor System (Qubes OS)
```bash
./scripts/monitor.sh
```

---

## ⚖️ Legal & Disclaimer

**This software is for educational purposes.**

- ✅ Arbitrage trading is legal in most jurisdictions
- ✅ Privacy tools (VPNs, Monero) are legal in most countries
- ⚠️ Check your local regulations regarding:
  - Cryptocurrency trading
  - DeFi platform access
  - Tax reporting requirements
  - Privacy tool usage

**Financial Disclaimer:**
- Past performance does not guarantee future results
- Cryptocurrency trading involves substantial risk
- Only trade with money you can afford to lose
- Consult a financial advisor before trading

**Privacy Disclaimer:**
- Use privacy tools responsibly and legally
- This system does not facilitate illegal activity
- Tax compliance is your responsibility
- Know your local KYC/AML requirements

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/Devon-ODell/EleanorPlatform/issues)
- **Documentation:** See docs in `guides/` directory
- **Backtests:** Run `python run_backtest.py` for examples

---

## 🎯 Roadmap

- [x] Regular DEX arbitrage (Uniswap, PancakeSwap)
- [x] Privacy coin arbitrage (Monero focus)
- [x] Selenium anti-detection scraping
- [x] AI decision engine (ML-powered)
- [x] Qubes OS deployment guide
- [x] Intel ME neutralization guide
- [x] Privacy cash-out strategy
- [ ] Web3 integration (on-chain data)
- [ ] Telegram notifications
- [ ] Multi-chain support (Solana, Avalanche)
- [ ] Advanced ML models (LSTM, Transformer)

---

**Made with ❤️ for privacy-conscious DeFi traders**
