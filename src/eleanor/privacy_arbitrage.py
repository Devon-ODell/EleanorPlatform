"""
Privacy Coin Arbitrage Detection and Execution
Specialized for Monero (XMR) and other privacy-preserving cryptocurrencies
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PrivacyArbitrageOpportunity:
    """Represents a privacy coin arbitrage opportunity"""
    timestamp: datetime
    pair: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    gross_profit_pct: float
    net_profit_pct: float
    optimal_size_usd: float
    expected_profit_usd: float
    buy_network_fee: float
    sell_network_fee: float
    buy_exchange_fee_pct: float
    sell_exchange_fee_pct: float
    buy_liquidity: float
    sell_liquidity: float
    confirmation_time_min: float
    risk_score: float  # Time risk due to confirmations

class PrivacyArbitrageDetector:
    """Detects arbitrage opportunities in privacy coin markets"""

    def __init__(self,
                 min_profit_pct: float = 1.0,  # Higher threshold for privacy coins
                 max_trade_size_usd: float = 5000,
                 min_trade_size_usd: float = 100,
                 max_confirmation_time_min: float = 45):
        """
        Initialize privacy coin arbitrage detector

        Args:
            min_profit_pct: Minimum net profit (higher than regular due to risks)
            max_trade_size_usd: Maximum trade size
            min_trade_size_usd: Minimum trade size
            max_confirmation_time_min: Maximum acceptable confirmation time
        """
        self.min_profit_pct = min_profit_pct
        self.max_trade_size_usd = max_trade_size_usd
        self.min_trade_size_usd = min_trade_size_usd
        self.max_confirmation_time_min = max_confirmation_time_min

    def find_opportunities(self, df: pd.DataFrame) -> List[PrivacyArbitrageOpportunity]:
        """
        Find arbitrage opportunities in privacy coin markets

        Privacy coin arbitrage considerations:
        - Higher spreads = more opportunities
        - Longer confirmation times = price movement risk
        - Lower liquidity = higher slippage
        - Multiple exchange types (instant, P2P, atomic swap)
        """
        opportunities = []

        # Group by timestamp and pair
        for (ts, pair), group in df.groupby(['timestamp', 'pair']):
            if len(group) < 2:
                continue

            # Find best buy (lowest price) and best sell (highest price)
            group = group.sort_values('price')
            buy_row = group.iloc[0]
            sell_row = group.iloc[-1]

            buy_exchange = buy_row['exchange']
            sell_exchange = sell_row['exchange']
            buy_price = buy_row['price']
            sell_price = sell_row['price']

            # Skip if same exchange
            if buy_exchange == sell_exchange:
                continue

            # Calculate gross profit
            gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100

            if gross_profit_pct <= 0:
                continue

            # Check confirmation time risk
            total_confirmation_time = buy_row['confirmation_time_min'] + sell_row['confirmation_time_min']
            if total_confirmation_time > self.max_confirmation_time_min:
                continue  # Too risky due to long confirmation times

            # Calculate optimal trade size
            optimal_size = self._calculate_optimal_size(
                buy_price=buy_price,
                sell_price=sell_price,
                buy_liquidity=buy_row['liquidity_usd'],
                sell_liquidity=sell_row['liquidity_usd']
            )

            if optimal_size < self.min_trade_size_usd:
                continue

            # Calculate net profit after all costs
            net_profit_pct, expected_profit_usd = self._calculate_net_profit(
                trade_size=optimal_size,
                buy_price=buy_price,
                sell_price=sell_price,
                buy_liquidity=buy_row['liquidity_usd'],
                sell_liquidity=sell_row['liquidity_usd'],
                buy_network_fee=buy_row['network_fee_usd'],
                sell_network_fee=sell_row['network_fee_usd'],
                buy_exchange_fee_pct=buy_row['exchange_fee_pct'],
                sell_exchange_fee_pct=sell_row['exchange_fee_pct']
            )

            # Calculate risk score based on confirmation time
            # Higher confirmation time = higher risk of price movement
            risk_score = self._calculate_risk_score(
                confirmation_time=total_confirmation_time,
                gross_profit_pct=gross_profit_pct,
                pair=pair
            )

            # Only accept if net profit meets threshold and risk is acceptable
            if net_profit_pct >= self.min_profit_pct and risk_score < 0.7:
                opportunity = PrivacyArbitrageOpportunity(
                    timestamp=ts,
                    pair=pair,
                    buy_exchange=buy_exchange,
                    sell_exchange=sell_exchange,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    gross_profit_pct=gross_profit_pct,
                    net_profit_pct=net_profit_pct,
                    optimal_size_usd=optimal_size,
                    expected_profit_usd=expected_profit_usd,
                    buy_network_fee=buy_row['network_fee_usd'],
                    sell_network_fee=sell_row['network_fee_usd'],
                    buy_exchange_fee_pct=buy_row['exchange_fee_pct'],
                    sell_exchange_fee_pct=sell_row['exchange_fee_pct'],
                    buy_liquidity=buy_row['liquidity_usd'],
                    sell_liquidity=sell_row['liquidity_usd'],
                    confirmation_time_min=total_confirmation_time,
                    risk_score=risk_score
                )
                opportunities.append(opportunity)

        return opportunities

    def _calculate_optimal_size(self,
                               buy_price: float,
                               sell_price: float,
                               buy_liquidity: float,
                               sell_liquidity: float) -> float:
        """
        Calculate optimal trade size for privacy coins

        Privacy coins have lower liquidity, so we need to be more conservative
        """
        # Use 1-3% of the smaller liquidity pool (vs 2% for regular DEXs)
        min_liquidity = min(buy_liquidity, sell_liquidity)
        optimal = min_liquidity * np.random.uniform(0.01, 0.03)

        # Ensure within bounds
        optimal = min(max(optimal, self.min_trade_size_usd), self.max_trade_size_usd)

        return optimal

    def _calculate_net_profit(self,
                             trade_size: float,
                             buy_price: float,
                             sell_price: float,
                             buy_liquidity: float,
                             sell_liquidity: float,
                             buy_network_fee: float,
                             sell_network_fee: float,
                             buy_exchange_fee_pct: float,
                             sell_exchange_fee_pct: float) -> Tuple[float, float]:
        """
        Calculate net profit for privacy coin arbitrage

        Privacy coin costs:
        - Network fees (Monero: $0.05-0.20, BTC: $1-5, ETH: $2-15)
        - Exchange fees (instant exchanges: 0.5-2%)
        - Higher slippage due to lower liquidity
        """
        from defi_data_privacy import calculate_privacy_coin_slippage

        # Calculate slippage (higher for privacy coins)
        buy_slippage = calculate_privacy_coin_slippage(trade_size, buy_liquidity)
        sell_slippage = calculate_privacy_coin_slippage(trade_size, sell_liquidity)

        # Effective prices after slippage
        effective_buy_price = buy_price * (1 + buy_slippage)
        effective_sell_price = sell_price * (1 - sell_slippage)

        # Exchange fees (already in percentage)
        buy_exchange_fee = trade_size * buy_exchange_fee_pct
        sell_exchange_fee = trade_size * sell_exchange_fee_pct

        # Network fees (fixed amount)
        network_fees = buy_network_fee + sell_network_fee

        # Total costs
        total_costs = buy_exchange_fee + sell_exchange_fee + network_fees

        # Calculate profit
        quantity = trade_size / effective_buy_price
        revenue = quantity * effective_sell_price
        cost = trade_size + total_costs

        profit_usd = revenue - cost
        profit_pct = (profit_usd / trade_size) * 100

        return profit_pct, profit_usd

    def _calculate_risk_score(self,
                             confirmation_time: float,
                             gross_profit_pct: float,
                             pair: str) -> float:
        """
        Calculate risk score for the trade

        Risk factors:
        - Longer confirmation time = higher price movement risk
        - Lower profit margin = less buffer for adverse price movement
        - Volatile pairs = higher risk

        Returns value between 0 (low risk) and 1 (high risk)
        """
        # Time risk: normalize to 0-1 (45 min = high risk)
        time_risk = min(confirmation_time / 45.0, 1.0)

        # Profit margin risk: lower profit = higher risk
        # Below 2% = high risk, above 5% = low risk
        if gross_profit_pct < 2:
            margin_risk = 0.8
        elif gross_profit_pct < 3:
            margin_risk = 0.5
        elif gross_profit_pct < 5:
            margin_risk = 0.3
        else:
            margin_risk = 0.1

        # Volatility risk: some coins are more volatile
        if 'DERO' in pair or 'XHV' in pair:
            volatility_risk = 0.7  # Higher risk for low-cap coins
        elif 'ZEC' in pair or 'SCRT' in pair:
            volatility_risk = 0.4
        else:  # XMR
            volatility_risk = 0.2  # Lower risk for XMR

        # Combined risk score (weighted average)
        risk_score = (time_risk * 0.4 + margin_risk * 0.3 + volatility_risk * 0.3)

        return risk_score


class PrivacyArbitrageExecutor:
    """Executes privacy coin arbitrage trades"""

    def __init__(self, initial_capital_usd: float = 15000):
        self.initial_capital = initial_capital_usd
        self.capital = initial_capital_usd
        self.trades = []
        self.total_profit = 0.0
        self.total_fees_paid = 0.0

    def execute_trade(self,
                     opportunity: PrivacyArbitrageOpportunity,
                     paper_trading: bool = True) -> Dict:
        """
        Execute privacy coin arbitrage trade

        For privacy coins, execution involves:
        1. Buy on exchange with lower price
        2. Wait for confirmations (XMR: ~20 min, BTC: ~10 min)
        3. Withdraw to wallet
        4. Deposit to sell exchange
        5. Wait for confirmations
        6. Sell at higher price
        """
        # Check capital
        if opportunity.optimal_size_usd > self.capital:
            return {
                'success': False,
                'reason': 'Insufficient capital',
                'capital': self.capital,
                'required': opportunity.optimal_size_usd
            }

        if paper_trading:
            result = self._paper_trade(opportunity)
        else:
            result = self._live_trade(opportunity)

        # Update stats
        if result['success']:
            self.capital += result['profit_usd']
            self.total_profit += result['profit_usd']
            self.total_fees_paid += result['total_fees']
            self.trades.append(result)

        return result

    def _paper_trade(self, opp: PrivacyArbitrageOpportunity) -> Dict:
        """Simulate privacy coin arbitrage execution"""

        # Higher failure rate for privacy coins due to:
        # - Confirmations taking too long
        # - Price moving against us
        # - Exchange issues (instant exchanges can fail)
        base_failure_rate = 0.03  # 3% base

        # Increase failure rate based on risk score
        failure_rate = base_failure_rate + (opp.risk_score * 0.07)

        if np.random.random() < failure_rate:
            return {
                'success': False,
                'reason': f'Trade failed (confirmation timeout or price moved)',
                'timestamp': opp.timestamp,
                'pair': opp.pair,
                'risk_score': opp.risk_score
            }

        # Simulate price movement during confirmation time
        # Price can move up to 0.5% per 10 minutes
        price_volatility = (opp.confirmation_time_min / 10.0) * 0.005
        price_movement = np.random.normal(0, price_volatility)

        # Adjust profit for price movement
        actual_profit = opp.expected_profit_usd * (1 + price_movement)

        total_fees = (opp.buy_network_fee + opp.sell_network_fee +
                     (opp.optimal_size_usd * opp.buy_exchange_fee_pct) +
                     (opp.optimal_size_usd * opp.sell_exchange_fee_pct))

        return {
            'success': True,
            'timestamp': opp.timestamp,
            'pair': opp.pair,
            'buy_exchange': opp.buy_exchange,
            'sell_exchange': opp.sell_exchange,
            'trade_size_usd': opp.optimal_size_usd,
            'profit_usd': actual_profit,
            'profit_pct': opp.net_profit_pct,
            'total_fees': total_fees,
            'confirmation_time_min': opp.confirmation_time_min,
            'risk_score': opp.risk_score,
            'capital_after': self.capital + actual_profit,
            'privacy_level': 'HIGH' if 'XMR' in opp.pair else 'MEDIUM'
        }

    def _live_trade(self, opp: PrivacyArbitrageOpportunity) -> Dict:
        """
        Execute live privacy coin arbitrage

        Would integrate with:
        - Monero wallet (monero-wallet-rpc)
        - Exchange APIs (TradeOgre, SideShift, etc.)
        - Atomic swap protocols
        """
        raise NotImplementedError("Live privacy coin trading requires wallet integration")

    def get_performance_summary(self) -> Dict:
        """Get trading performance summary"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_profit_usd': 0.0,
                'total_return_pct': 0.0,
                'win_rate': 0.0,
                'avg_profit_per_trade': 0.0,
                'total_fees_paid': 0.0,
                'final_capital': self.capital,
                'xmr_trades': 0,
                'avg_confirmation_time': 0.0
            }

        successful_trades = [t for t in self.trades if t['success']]
        profitable_trades = [t for t in successful_trades if t['profit_usd'] > 0]
        xmr_trades = [t for t in successful_trades if 'XMR' in t['pair']]

        avg_confirmation = np.mean([t['confirmation_time_min'] for t in successful_trades])

        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_trades': len(successful_trades),
            'total_profit_usd': self.total_profit,
            'total_return_pct': (self.total_profit / self.initial_capital) * 100,
            'win_rate': len(profitable_trades) / len(successful_trades) * 100 if successful_trades else 0,
            'avg_profit_per_trade': self.total_profit / len(successful_trades) if successful_trades else 0,
            'total_fees_paid': self.total_fees_paid,
            'net_profit_after_fees': self.total_profit - self.total_fees_paid,
            'xmr_trades': len(xmr_trades),
            'xmr_percentage': len(xmr_trades) / len(successful_trades) * 100 if successful_trades else 0,
            'avg_confirmation_time': avg_confirmation,
            'avg_risk_score': np.mean([t['risk_score'] for t in successful_trades]),
            'trades': successful_trades
        }
