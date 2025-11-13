"""
DeFi Arbitrage Detection and Execution
Identifies and executes profitable arbitrage opportunities across DEXs
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity"""
    timestamp: datetime
    pair: str
    buy_dex: str
    sell_dex: str
    buy_price: float
    sell_price: float
    gross_profit_pct: float
    net_profit_pct: float
    optimal_size_usd: float
    expected_profit_usd: float
    buy_gas_cost: float
    sell_gas_cost: float
    buy_liquidity: float
    sell_liquidity: float

class ArbitrageDetector:
    """Detects arbitrage opportunities across DEXs"""

    def __init__(self,
                 min_profit_pct: float = 0.5,
                 max_trade_size_usd: float = 10000,
                 min_trade_size_usd: float = 100):
        """
        Initialize arbitrage detector

        Args:
            min_profit_pct: Minimum net profit percentage to execute (after costs)
            max_trade_size_usd: Maximum trade size in USD
            min_trade_size_usd: Minimum trade size in USD
        """
        self.min_profit_pct = min_profit_pct
        self.max_trade_size_usd = max_trade_size_usd
        self.min_trade_size_usd = min_trade_size_usd

    def find_opportunities(self, df: pd.DataFrame) -> List[ArbitrageOpportunity]:
        """
        Find all arbitrage opportunities in the given data

        Args:
            df: DataFrame with columns [timestamp, dex, pair, price, liquidity_usd, gas_cost_usd]

        Returns:
            List of ArbitrageOpportunity objects
        """
        opportunities = []

        # Group by timestamp and pair
        for (ts, pair), group in df.groupby(['timestamp', 'pair']):
            # Need at least 2 DEXs to arbitrage
            if len(group) < 2:
                continue

            # Find best buy (lowest price) and best sell (highest price)
            group = group.sort_values('price')
            buy_row = group.iloc[0]  # Lowest price (buy here)
            sell_row = group.iloc[-1]  # Highest price (sell here)

            buy_dex = buy_row['dex']
            sell_dex = sell_row['dex']
            buy_price = buy_row['price']
            sell_price = sell_row['price']

            # Calculate gross profit percentage
            gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100

            # Skip if not profitable
            if gross_profit_pct <= 0:
                continue

            # Calculate optimal trade size
            optimal_size = self._calculate_optimal_size(
                buy_price=buy_price,
                sell_price=sell_price,
                buy_liquidity=buy_row['liquidity_usd'],
                sell_liquidity=sell_row['liquidity_usd'],
                buy_gas=buy_row['gas_cost_usd'],
                sell_gas=sell_row['gas_cost_usd']
            )

            # Skip if optimal size is outside bounds
            if optimal_size < self.min_trade_size_usd or optimal_size > self.max_trade_size_usd:
                continue

            # Calculate net profit after costs
            net_profit_pct, expected_profit_usd = self._calculate_net_profit(
                trade_size=optimal_size,
                buy_price=buy_price,
                sell_price=sell_price,
                buy_liquidity=buy_row['liquidity_usd'],
                sell_liquidity=sell_row['liquidity_usd'],
                buy_gas=buy_row['gas_cost_usd'],
                sell_gas=sell_row['gas_cost_usd']
            )

            # Only record if net profit exceeds minimum
            if net_profit_pct >= self.min_profit_pct:
                opportunity = ArbitrageOpportunity(
                    timestamp=ts,
                    pair=pair,
                    buy_dex=buy_dex,
                    sell_dex=sell_dex,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    gross_profit_pct=gross_profit_pct,
                    net_profit_pct=net_profit_pct,
                    optimal_size_usd=optimal_size,
                    expected_profit_usd=expected_profit_usd,
                    buy_gas_cost=buy_row['gas_cost_usd'],
                    sell_gas_cost=sell_row['gas_cost_usd'],
                    buy_liquidity=buy_row['liquidity_usd'],
                    sell_liquidity=sell_row['liquidity_usd']
                )
                opportunities.append(opportunity)

        return opportunities

    def _calculate_optimal_size(self,
                               buy_price: float,
                               sell_price: float,
                               buy_liquidity: float,
                               sell_liquidity: float,
                               buy_gas: float,
                               sell_gas: float) -> float:
        """
        Calculate optimal trade size to maximize profit

        This is a simplified calculation. In reality, you'd solve:
        max_profit = (sell_price * (1 - slippage_sell) - buy_price * (1 + slippage_buy)) * qty - gas_costs

        For simplicity, we use a fraction of the minimum liquidity
        """
        # Use 2% of the smaller liquidity pool to minimize slippage
        min_liquidity = min(buy_liquidity, sell_liquidity)
        optimal = min_liquidity * 0.02

        # Ensure within bounds
        optimal = min(max(optimal, self.min_trade_size_usd), self.max_trade_size_usd)

        return optimal

    def _calculate_net_profit(self,
                             trade_size: float,
                             buy_price: float,
                             sell_price: float,
                             buy_liquidity: float,
                             sell_liquidity: float,
                             buy_gas: float,
                             sell_gas: float) -> Tuple[float, float]:
        """
        Calculate net profit percentage and USD amount after all costs

        Accounts for:
        - Slippage on both buy and sell sides
        - Gas costs for both transactions
        - Trading fees (typically 0.3% per swap on most DEXs)
        """
        try:
            from .defi_data import calculate_slippage
        except ImportError:
            from defi_data import calculate_slippage

        # Calculate slippage
        buy_slippage = calculate_slippage(trade_size, buy_liquidity)
        sell_slippage = calculate_slippage(trade_size, sell_liquidity)

        # Effective prices after slippage
        effective_buy_price = buy_price * (1 + buy_slippage)
        effective_sell_price = sell_price * (1 - sell_slippage)

        # Trading fees (0.3% is standard for Uniswap/Sushi)
        trading_fee_pct = 0.003
        buy_fee = trade_size * trading_fee_pct
        sell_fee = trade_size * trading_fee_pct

        # Total costs
        gas_costs = buy_gas + sell_gas
        fee_costs = buy_fee + sell_fee

        # Calculate profit
        quantity = trade_size / effective_buy_price  # How much token we buy
        revenue = quantity * effective_sell_price     # Revenue from selling
        cost = trade_size + fee_costs + gas_costs     # Total cost

        profit_usd = revenue - cost
        profit_pct = (profit_usd / trade_size) * 100

        return profit_pct, profit_usd


class ArbitrageExecutor:
    """Executes arbitrage trades (paper trading and live)"""

    def __init__(self, initial_capital_usd: float = 15000):
        self.initial_capital = initial_capital_usd
        self.capital = initial_capital_usd
        self.trades = []
        self.total_profit = 0.0
        self.total_gas_paid = 0.0

    def execute_trade(self, opportunity: ArbitrageOpportunity, paper_trading: bool = True) -> Dict:
        """
        Execute an arbitrage trade

        Args:
            opportunity: ArbitrageOpportunity to execute
            paper_trading: If True, simulate trade; if False, execute on-chain

        Returns:
            Dictionary with trade results
        """
        # Check if we have enough capital
        if opportunity.optimal_size_usd > self.capital:
            return {
                'success': False,
                'reason': 'Insufficient capital',
                'capital': self.capital,
                'required': opportunity.optimal_size_usd
            }

        if paper_trading:
            # Simulate the trade
            result = self._paper_trade(opportunity)
        else:
            # Execute on-chain (placeholder for Hummingbot integration)
            result = self._live_trade(opportunity)

        # Update capital and stats
        if result['success']:
            self.capital += result['profit_usd']
            self.total_profit += result['profit_usd']
            self.total_gas_paid += result['gas_paid']
            self.trades.append(result)

        return result

    def _paper_trade(self, opp: ArbitrageOpportunity) -> Dict:
        """Simulate arbitrage trade execution"""
        # Add some execution noise (1-3% chance of failure)
        if np.random.random() < 0.02:
            return {
                'success': False,
                'reason': 'Transaction reverted or front-run',
                'timestamp': opp.timestamp,
                'pair': opp.pair
            }

        return {
            'success': True,
            'timestamp': opp.timestamp,
            'pair': opp.pair,
            'buy_dex': opp.buy_dex,
            'sell_dex': opp.sell_dex,
            'trade_size_usd': opp.optimal_size_usd,
            'profit_usd': opp.expected_profit_usd,
            'profit_pct': opp.net_profit_pct,
            'gas_paid': opp.buy_gas_cost + opp.sell_gas_cost,
            'capital_after': self.capital + opp.expected_profit_usd
        }

    def _live_trade(self, opp: ArbitrageOpportunity) -> Dict:
        """
        Execute live arbitrage trade via Hummingbot

        This would integrate with Hummingbot's API to:
        1. Submit buy order on buy_dex
        2. Wait for confirmation
        3. Submit sell order on sell_dex
        4. Wait for confirmation
        """
        # Placeholder - in production, call Hummingbot API
        raise NotImplementedError("Live trading requires Hummingbot integration")

    def get_performance_summary(self) -> Dict:
        """Get trading performance summary"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_profit_usd': 0.0,
                'total_return_pct': 0.0,
                'win_rate': 0.0,
                'avg_profit_per_trade': 0.0,
                'total_gas_paid': 0.0,
                'final_capital': self.capital
            }

        successful_trades = [t for t in self.trades if t['success']]
        profitable_trades = [t for t in successful_trades if t['profit_usd'] > 0]

        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_trades': len(successful_trades),
            'total_profit_usd': self.total_profit,
            'total_return_pct': (self.total_profit / self.initial_capital) * 100,
            'win_rate': len(profitable_trades) / len(successful_trades) * 100 if successful_trades else 0,
            'avg_profit_per_trade': self.total_profit / len(successful_trades) if successful_trades else 0,
            'total_gas_paid': self.total_gas_paid,
            'net_profit_after_gas': self.total_profit - self.total_gas_paid,
            'trades': successful_trades
        }
