"""
DeFi Arbitrage Backtesting Framework
Runs historical backtests to evaluate arbitrage strategy performance
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import matplotlib.pyplot as plt
from pathlib import Path

try:
    from .defi_data import DEXDataFetcher, calculate_slippage
    from .defi_arbitrage import ArbitrageDetector, ArbitrageExecutor
except ImportError:
    from defi_data import DEXDataFetcher, calculate_slippage
    from defi_arbitrage import ArbitrageDetector, ArbitrageExecutor


class DeFiBacktest:
    """Backtesting engine for DeFi arbitrage strategies"""

    def __init__(self,
                 initial_capital: float = 15000,
                 min_profit_pct: float = 0.5,
                 max_trade_size: float = 10000,
                 min_trade_size: float = 100):
        """
        Initialize backtest

        Args:
            initial_capital: Starting capital in USD
            min_profit_pct: Minimum profit percentage threshold
            max_trade_size: Maximum trade size in USD
            min_trade_size: Minimum trade size in USD
        """
        self.initial_capital = initial_capital
        self.data_fetcher = DEXDataFetcher()
        self.detector = ArbitrageDetector(
            min_profit_pct=min_profit_pct,
            max_trade_size_usd=max_trade_size,
            min_trade_size_usd=min_trade_size
        )
        self.executor = ArbitrageExecutor(initial_capital_usd=initial_capital)
        self.results = None

    def run(self,
            start_date: datetime,
            end_date: datetime,
            interval_minutes: int = 5) -> Dict:
        """
        Run backtest over specified date range

        Args:
            start_date: Start of backtest period
            end_date: End of backtest period
            interval_minutes: Data sampling interval in minutes

        Returns:
            Dictionary with backtest results
        """
        print("=" * 70)
        print("DeFi ARBITRAGE BACKTESTING FRAMEWORK")
        print("=" * 70)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Min Profit Threshold: {self.detector.min_profit_pct}%")
        print("=" * 70)
        print()

        # Step 1: Generate historical data
        print("📊 Step 1: Generating historical DEX price data...")
        df = self.data_fetcher.generate_historical_data(
            start_date=start_date,
            end_date=end_date,
            interval_minutes=interval_minutes
        )
        print(f"✅ Generated {len(df)} price points\n")

        # Step 2: Detect arbitrage opportunities
        print("🔍 Step 2: Scanning for arbitrage opportunities...")
        opportunities = self.detector.find_opportunities(df)
        print(f"✅ Found {len(opportunities)} profitable opportunities\n")

        if not opportunities:
            print("⚠️  No profitable opportunities found. Try adjusting parameters.")
            return self._empty_results()

        # Step 3: Execute trades (paper trading)
        print("💰 Step 3: Executing arbitrage trades (paper trading)...")
        executed_count = 0
        for opp in opportunities:
            result = self.executor.execute_trade(opp, paper_trading=True)
            if result['success']:
                executed_count += 1
                if executed_count % 100 == 0:
                    print(f"   Executed {executed_count} trades... Capital: ${self.executor.capital:,.2f}")

        print(f"✅ Successfully executed {executed_count} trades\n")

        # Step 4: Calculate performance metrics
        print("📈 Step 4: Calculating performance metrics...")
        performance = self.executor.get_performance_summary()
        performance['sharpe_ratio'] = self._calculate_sharpe_ratio()
        performance['max_drawdown'] = self._calculate_max_drawdown()
        performance['calmar_ratio'] = performance['total_return_pct'] / abs(performance['max_drawdown']) if performance['max_drawdown'] != 0 else 0

        self.results = performance
        print("✅ Performance analysis complete\n")

        # Display results
        self._display_results()

        return performance

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from trade returns"""
        if not self.executor.trades:
            return 0.0

        # Calculate returns per trade
        returns = [t['profit_pct'] / 100 for t in self.executor.trades if t['success']]

        if len(returns) < 2:
            return 0.0

        # Annualize (assuming ~100 trades per day, 252 trading days)
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # Sharpe ratio (assuming 0% risk-free rate for simplicity)
        sharpe = (mean_return / std_return) * np.sqrt(len(returns))

        return sharpe

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown percentage"""
        if not self.executor.trades:
            return 0.0

        # Calculate running capital
        capital_history = [self.initial_capital]
        current_capital = self.initial_capital

        for trade in self.executor.trades:
            if trade['success']:
                current_capital = trade['capital_after']
                capital_history.append(current_capital)

        # Calculate drawdowns
        peak = capital_history[0]
        max_dd = 0.0

        for capital in capital_history:
            if capital > peak:
                peak = capital
            dd = ((capital - peak) / peak) * 100
            if dd < max_dd:
                max_dd = dd

        return max_dd

    def _display_results(self):
        """Display formatted backtest results"""
        perf = self.results

        print("=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(f"Initial Capital:        ${perf['initial_capital']:,.2f}")
        print(f"Final Capital:          ${perf['final_capital']:,.2f}")
        print(f"Total Profit:           ${perf['total_profit_usd']:,.2f}")
        print(f"Total Return:           {perf['total_return_pct']:.2f}%")
        print("-" * 70)
        print(f"Total Trades:           {perf['total_trades']}")
        print(f"Win Rate:               {perf['win_rate']:.2f}%")
        print(f"Avg Profit/Trade:       ${perf['avg_profit_per_trade']:.2f}")
        print("-" * 70)
        print(f"Total Gas Fees:         ${perf['total_gas_paid']:,.2f}")
        print(f"Net Profit After Gas:   ${perf['net_profit_after_gas']:,.2f}")
        print("-" * 70)
        print(f"Sharpe Ratio:           {perf['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:           {perf['max_drawdown']:.2f}%")
        print(f"Calmar Ratio:           {perf['calmar_ratio']:.2f}")
        print("=" * 70)

    def _empty_results(self) -> Dict:
        """Return empty results structure"""
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.initial_capital,
            'total_trades': 0,
            'total_profit_usd': 0.0,
            'total_return_pct': 0.0,
            'win_rate': 0.0,
            'avg_profit_per_trade': 0.0,
            'total_gas_paid': 0.0,
            'net_profit_after_gas': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'calmar_ratio': 0.0,
            'trades': []
        }

    def save_results(self, output_dir: str = "./results"):
        """Save backtest results to files"""
        if not self.results:
            print("No results to save. Run backtest first.")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = output_path / f"backtest_summary_{timestamp}.txt"

        with open(summary_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("DeFi ARBITRAGE BACKTEST SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            for key, value in self.results.items():
                if key != 'trades':
                    f.write(f"{key}: {value}\n")

        # Save trade history
        if self.results['trades']:
            trades_df = pd.DataFrame(self.results['trades'])
            trades_file = output_path / f"trade_history_{timestamp}.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"✅ Saved trade history to: {trades_file}")

        print(f"✅ Saved summary to: {summary_file}")

    def plot_performance(self, output_dir: str = "./results"):
        """Plot performance charts"""
        if not self.executor.trades:
            print("No trades to plot")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Calculate equity curve
        timestamps = []
        capital_values = []
        current_capital = self.initial_capital

        for trade in self.executor.trades:
            if trade['success']:
                timestamps.append(trade['timestamp'])
                current_capital = trade['capital_after']
                capital_values.append(current_capital)

        if not timestamps:
            print("No successful trades to plot")
            return

        # Create equity curve plot
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Equity curve
        axes[0].plot(timestamps, capital_values, linewidth=2, color='#2E86AB')
        axes[0].axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5)
        axes[0].set_title('Equity Curve', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Capital (USD)', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylim(bottom=0)

        # Trade profits
        trade_profits = [t['profit_usd'] for t in self.executor.trades if t['success']]
        axes[1].bar(range(len(trade_profits)), trade_profits, color='green', alpha=0.6)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1].set_title('Trade Profits', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Trade Number', fontsize=12)
        axes[1].set_ylabel('Profit (USD)', fontsize=12)
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_file = output_path / f"performance_{timestamp}.png"
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"✅ Saved performance chart to: {plot_file}")
        plt.close()


def main():
    """Main entry point for backtesting"""
    # Configuration
    INITIAL_CAPITAL = 15000  # $15,000
    START_DATE = datetime(2025, 8, 1, tzinfo=timezone.utc)  # Aug 1, 2025
    END_DATE = datetime(2025, 10, 31, 23, 59, tzinfo=timezone.utc)  # Oct 31, 2025 (3 months)
    MIN_PROFIT_PCT = 0.2  # 0.2% minimum profit after all costs
    MAX_TRADE_SIZE = 5000  # Maximum $5,000 per trade
    MIN_TRADE_SIZE = 100   # Minimum $100 per trade

    # Run backtest
    backtest = DeFiBacktest(
        initial_capital=INITIAL_CAPITAL,
        min_profit_pct=MIN_PROFIT_PCT,
        max_trade_size=MAX_TRADE_SIZE,
        min_trade_size=MIN_TRADE_SIZE
    )

    results = backtest.run(
        start_date=START_DATE,
        end_date=END_DATE,
        interval_minutes=5  # Check for opportunities every 5 minutes
    )

    # Save results and plots
    backtest.save_results()
    backtest.plot_performance()

    print("\n🎉 Backtest complete!")
    print(f"\n💵 You could have turned ${INITIAL_CAPITAL:,} into ${results['final_capital']:,.2f}")
    print(f"   That's a {results['total_return_pct']:.2f}% return in 3 months!")


if __name__ == "__main__":
    main()
