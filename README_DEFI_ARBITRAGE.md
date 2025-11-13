# Eleanor Platform - DeFi Arbitrage Backtesting

## Overview

This project implements a DeFi arbitrage trading system that exploits price differences across multiple decentralized exchanges (DEXs). The system includes:

- **Multi-DEX Price Monitoring**: Tracks prices across Uniswap V3, SushiSwap, PancakeSwap, and Curve
- **Arbitrage Detection**: Identifies profitable opportunities accounting for gas fees and slippage
- **Backtesting Framework**: Simulates historical performance with realistic market conditions
- **Paper Trading**: Live paper trading simulation for real-time testing
- **Hummingbot Integration**: Configuration for live trading execution

## Quick Start

### 1. Run 3-Month Backtest ($15,000 Starting Capital)

```bash
python run_backtest.py
```

This will:
- Generate 3 months of historical DEX price data (Aug-Oct 2025)
- Detect arbitrage opportunities across 4 DEXs and 12 trading pairs
- Execute paper trades with realistic slippage and gas costs
- Generate performance report with P&L, Sharpe ratio, and statistics

### 2. Run Paper Trading (24 hours)

```bash
cd src/eleanor
python run_paper_trading.py --capital 15000 --duration 24
```

Options:
- `--capital`: Initial capital in USD (default: 15000)
- `--min-profit`: Minimum profit % threshold (default: 0.5)
- `--interval`: Check interval in seconds (default: 30)
- `--duration`: Duration in hours (default: 24)
- `--max-trade-size`: Max trade size in USD (default: 5000)

### 3. View Results

Results are saved to:
- `./results/backtest_summary_*.txt` - Performance summary
- `./results/trade_history_*.csv` - Detailed trade log
- `./results/performance_*.png` - Equity curve and profit charts

## Strategy Details

### Supported Trading Pairs

- ETH/USDT, ETH/USDC, ETH/DAI
- BTC/USDT, BTC/ETH
- MATIC/USDT, MATIC/ETH
- LINK/ETH, LINK/USDT
- UNI/ETH, UNI/USDT
- AAVE/ETH, AAVE/USDT

### DEXs Monitored

1. **Uniswap V3** (Ethereum) - Concentrated liquidity, tightest spreads
2. **SushiSwap** (Ethereum) - Medium spreads
3. **PancakeSwap** (BSC) - Lower gas fees, wider spreads
4. **Curve** (Ethereum) - Best for stablecoin pairs

### Cost Model

The backtest accounts for:
- **Gas Fees**: $5-30 per transaction (varies by DEX and network)
- **Trading Fees**: 0.3% per swap (standard DEX fee)
- **Slippage**: Dynamic based on trade size vs liquidity
- **Front-running Risk**: 1-3% chance of transaction failure

### Profit Calculation

```
Net Profit = (Sell Price - Buy Price) × Quantity
           - Buy Slippage
           - Sell Slippage
           - Trading Fees (0.6% total)
           - Gas Fees (2 transactions)
```

Only opportunities with net profit > 0.5% are executed.

## Architecture

### Core Modules

```
src/eleanor/
├── defi_data.py          # DEX data fetching and generation
├── defi_arbitrage.py     # Arbitrage detection and execution
├── backtest_defi.py      # Backtesting framework
└── run_paper_trading.py  # Paper trading session manager
```

### Hummingbot Integration

Configuration files:
- `conf/hummingbot/conf_client.yaml` - Client settings
- `conf/hummingbot/conf_arb_strategy.yml` - Arbitrage strategy config

To run with Hummingbot:
```bash
docker-compose -f compose/docker-compose.yaml up -d
```

## Performance Metrics

The backtest calculates:

- **Total Return %**: Overall profit percentage
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest capital decline
- **Calmar Ratio**: Return / Max Drawdown
- **Win Rate**: Percentage of profitable trades
- **Average Profit per Trade**: Mean profit across all trades

## Configuration

### Backtest Parameters

Edit `src/eleanor/backtest_defi.py`:

```python
INITIAL_CAPITAL = 15000      # Starting capital
START_DATE = datetime(2025, 8, 1)
END_DATE = datetime(2025, 10, 31)
MIN_PROFIT_PCT = 0.3         # Minimum 0.3% profit
MAX_TRADE_SIZE = 5000        # Max $5,000 per trade
MIN_TRADE_SIZE = 100         # Min $100 per trade
```

### DEX Selection

Edit `src/eleanor/defi_data.py`:

```python
self.dexs = ['uniswap_v3', 'sushiswap', 'pancakeswap', 'curve']
```

### Trading Pairs

Edit `src/eleanor/defi_data.py`:

```python
self.pairs = [
    'ETH/USDT', 'ETH/USDC', 'ETH/DAI',
    'BTC/USDT', 'BTC/ETH',
    # Add more pairs...
]
```

## Risk Disclaimer

⚠️ **IMPORTANT**: This is a backtesting and paper trading system. Results are based on simulated data and may not reflect actual market conditions. Real DeFi arbitrage involves:

- **Smart contract risk**: Protocol bugs and exploits
- **Network congestion**: Failed transactions during high gas
- **Front-running**: MEV bots may compete for the same opportunities
- **Impermanent loss**: If providing liquidity
- **Regulatory risk**: Compliance with local laws

Always start with paper trading and small amounts before scaling up.

## Live Trading (Advanced)

To enable live trading:

1. Configure Hummingbot with your DEX API keys
2. Set up Ethereum wallet with funds
3. Update `conf/hummingbot/conf_arb_strategy.yml`
4. Start Hummingbot: `docker-compose up`
5. Monitor trades via Hummingbot dashboard

**Note**: Live trading requires extensive testing and risk management.

## Troubleshooting

### "No profitable opportunities found"

- Lower `MIN_PROFIT_PCT` in backtest_defi.py
- Increase `MAX_TRADE_SIZE` to allow larger trades
- Check if data generation is working correctly

### "Import errors"

Install dependencies:
```bash
pip install -r requirements.txt
```

Or install package in development mode:
```bash
pip install -e src/eleanor
```

## Next Steps

1. **Run the backtest**: See potential returns over 3 months
2. **Analyze results**: Review trade history and equity curve
3. **Adjust parameters**: Optimize for your risk tolerance
4. **Paper trade**: Test with simulated real-time data
5. **Live trading**: Deploy with Hummingbot (advanced users)

## Support

For issues or questions:
- Review the code comments in each module
- Check Hummingbot documentation: https://docs.hummingbot.org
- Open an issue in the project repository

---

**Happy Trading! 🚀**
