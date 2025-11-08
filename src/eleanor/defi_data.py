"""
DeFi Data Fetching Module
Fetches price data from multiple DEXs for arbitrage opportunities
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
import requests
import time

class DEXDataFetcher:
    """Fetches price data from multiple decentralized exchanges"""

    def __init__(self):
        self.dexs = ['uniswap_v3', 'sushiswap', 'pancakeswap', 'curve']
        # Popular trading pairs for arbitrage
        self.pairs = [
            'ETH/USDT', 'ETH/USDC', 'ETH/DAI',
            'BTC/USDT', 'BTC/ETH',
            'MATIC/USDT', 'MATIC/ETH',
            'LINK/ETH', 'LINK/USDT',
            'UNI/ETH', 'UNI/USDT',
            'AAVE/ETH', 'AAVE/USDT'
        ]

    def generate_historical_data(self,
                                start_date: datetime,
                                end_date: datetime,
                                interval_minutes: int = 5) -> pd.DataFrame:
        """
        Generate realistic historical DEX price data for backtesting

        In production, this would fetch from TheGraph, Dune Analytics, or DEX APIs
        For now, we generate realistic synthetic data with arbitrage opportunities
        """
        data = []
        current = start_date

        # Base prices (realistic 2025 levels)
        base_prices = {
            'ETH/USDT': 3500.0,
            'ETH/USDC': 3500.0,
            'ETH/DAI': 3500.0,
            'BTC/USDT': 65000.0,
            'BTC/ETH': 18.57,  # BTC/ETH ratio
            'MATIC/USDT': 1.2,
            'MATIC/ETH': 0.00034,
            'LINK/ETH': 0.0042,
            'LINK/USDT': 14.7,
            'UNI/ETH': 0.0018,
            'UNI/USDT': 6.3,
            'AAVE/ETH': 0.042,
            'AAVE/USDT': 147.0
        }

        # Track price evolution with random walk
        prices = {pair: base_prices[pair] for pair in self.pairs}

        print(f"Generating historical data from {start_date} to {end_date}...")

        while current <= end_date:
            timestamp = current

            # Update prices with random walk + some trends
            for pair in self.pairs:
                # Random walk with drift
                drift = 0.0001  # Slight upward trend
                volatility = 0.002  # 0.2% volatility per 5min
                change = np.random.normal(drift, volatility)
                prices[pair] *= (1 + change)

                # Generate prices for each DEX with realistic spreads
                for dex in self.dexs:
                    # Different DEXs have different liquidity/spreads
                    # Base spread factors
                    base_spread = {
                        'uniswap_v3': 0.0005,    # 0.05% base
                        'sushiswap': 0.0015,     # 0.15% base
                        'pancakeswap': 0.0025,   # 0.25% base (BSC, different network)
                        'curve': 0.0008          # 0.08% base
                    }[dex]

                    # Add randomness and occasional larger spreads (5% chance of 2-3x wider spread)
                    if np.random.random() < 0.05:
                        spread_factor = base_spread * np.random.uniform(2.0, 3.0)
                    else:
                        spread_factor = base_spread * np.random.uniform(0.5, 1.5)

                    # Add DEX-specific spread and noise (can be positive or negative)
                    noise = np.random.normal(0, spread_factor)
                    dex_price = prices[pair] * (1 + noise)

                    # Add liquidity depth (affects slippage)
                    liquidity_usd = np.random.uniform(500000, 5000000)

                    # Gas costs vary by network
                    gas_cost_usd = {
                        'uniswap_v3': np.random.uniform(5, 20),
                        'sushiswap': np.random.uniform(5, 20),
                        'pancakeswap': np.random.uniform(0.1, 0.5),  # BSC is cheaper
                        'curve': np.random.uniform(10, 30)
                    }[dex]

                    data.append({
                        'timestamp': timestamp,
                        'dex': dex,
                        'pair': pair,
                        'price': dex_price,
                        'liquidity_usd': liquidity_usd,
                        'gas_cost_usd': gas_cost_usd,
                        'spread_bps': spread_factor * 10000  # basis points
                    })

            current += timedelta(minutes=interval_minutes)

        df = pd.DataFrame(data)
        df = df.sort_values('timestamp')
        print(f"Generated {len(df)} data points across {len(self.pairs)} pairs and {len(self.dexs)} DEXs")
        return df

    def fetch_live_prices(self, pair: str) -> Dict[str, float]:
        """
        Fetch live prices from DEXs (placeholder for production use)

        In production, integrate with:
        - 1inch API for aggregated prices
        - DEX-specific APIs (Uniswap, SushiSwap, etc.)
        - Web3 direct contract calls
        """
        # This would call actual DEX APIs
        # For now, return mock data
        return {dex: 0.0 for dex in self.dexs}


def calculate_slippage(trade_size_usd: float, liquidity_usd: float) -> float:
    """
    Calculate slippage based on trade size and available liquidity

    Uses simplified constant product AMM formula: x * y = k
    Slippage increases with trade size relative to pool size
    """
    if liquidity_usd <= 0:
        return 0.10  # 10% slippage for no liquidity (edge case)

    # Percentage of pool this trade represents
    pool_impact = trade_size_usd / liquidity_usd

    # Slippage formula: approximately linear for small trades, exponential for large
    if pool_impact < 0.01:  # < 1% of pool
        slippage = pool_impact * 0.5
    elif pool_impact < 0.05:  # 1-5% of pool
        slippage = 0.005 + (pool_impact - 0.01) * 0.8
    else:  # > 5% of pool
        slippage = 0.037 + (pool_impact - 0.05) * 2.0

    return min(slippage, 0.25)  # Cap at 25% slippage
