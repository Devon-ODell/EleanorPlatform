#!/usr/bin/env python3
"""
Privacy Coin Arbitrage Backtest Runner
Focuses on Monero (XMR) and privacy-preserving cryptocurrencies
"""

import sys
import os
from pathlib import Path

# Add src/eleanor to path
src_path = Path(__file__).parent / "src" / "eleanor"
sys.path.insert(0, str(src_path))

# Change to the script directory
os.chdir(str(src_path))

if __name__ == "__main__":
    print("🔒 Eleanor Platform - Privacy Coin Arbitrage Backtest")
    print("   Focusing on Monero (XMR) and Privacy Coins")
    print("   Testing $15,000 over 3 months (Aug-Oct 2025)\n")

    from backtest_privacy import main
    main()
