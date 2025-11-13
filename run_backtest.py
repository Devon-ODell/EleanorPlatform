#!/usr/bin/env python3
"""
Quick runner for DeFi Arbitrage Backtesting

This script runs a 3-month backtest with $15,000 starting capital
to demonstrate potential returns from DeFi arbitrage trading.
"""

import sys
import os
from pathlib import Path

# Add src/eleanor to path
src_path = Path(__file__).parent / "src" / "eleanor"
sys.path.insert(0, str(src_path))

# Change to the script directory to ensure proper module loading
os.chdir(str(src_path))

if __name__ == "__main__":
    print("🚀 Eleanor Platform - DeFi Arbitrage Backtest")
    print("   Testing $15,000 over 3 months (Aug-Oct 2025)\n")

    from backtest_defi import main
    main()
