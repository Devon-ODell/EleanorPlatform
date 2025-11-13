"""
Privacy Coin Arbitrage Backtesting Framework
Specialized for Monero (XMR) and privacy-preserving cryptocurrencies
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

try:
    from .defi_data_privacy import PrivacyCoinDataFetcher, get_privacy_coin_info
    from .privacy_arbitrage import PrivacyArbitrageDetector, PrivacyArbitrageExecutor
except ImportError:
    from defi_data_privacy import PrivacyCoinDataFetcher, get_privacy_coin_info
    from privacy_arbitrage import PrivacyArbitrageDetector, PrivacyArbitrageExecutor


class PrivacyCoinBacktest:
    """Backtesting engine for privacy coin arbitrage"""

    def __init__(self,
                 initial_capital: float = 15000,
                 min_profit_pct: float = 1.0,
                 max_trade_size: float = 5000,
                 min_trade_size: float = 100):
        """
        Initialize privacy coin backtest

        Args:
            initial_capital: Starting capital in USD
            min_profit_pct: Minimum profit threshold (higher for privacy coins)
            max_trade_size: Maximum trade size
            min_trade_size: Minimum trade size
        """
        self.initial_capital = initial_capital
        self.data_fetcher = PrivacyCoinDataFetcher()
        self.detector = PrivacyArbitrageDetector(
            min_profit_pct=min_profit_pct,
            max_trade_size_usd=max_trade_size,
            min_trade_size_usd=min_trade_size
        )
        self.executor = PrivacyArbitrageExecutor(initial_capital_usd=initial_capital)
        self.results = None

    def run(self,
            start_date: datetime,
            end_date: datetime,
            interval_minutes: int = 10) -> Dict:
        """Run privacy coin arbitrage backtest"""

        print("=" * 70)
        print("PRIVACY COIN ARBITRAGE BACKTESTING")
        print("=" * 70)
        print(f"💰 Initial Capital: ${self.initial_capital:,.2f}")
        print(f"📅 Period: {start_date.date()} to {end_date.date()}")
        print(f"🎯 Min Profit Threshold: {self.detector.min_profit_pct}%")
        print(f"🔒 Privacy Focus: Monero (XMR) + Privacy Coins")
        print("=" * 70)
        print()

        # Step 1: Generate historical data
        print("📊 Step 1: Generating privacy coin exchange data...")
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

        # Show opportunity breakdown
        self._show_opportunity_breakdown(opportunities)

        # Step 3: Execute trades
        print("\n💰 Step 3: Executing arbitrage trades (paper trading)...")
        executed_count = 0
        failed_count = 0

        for opp in opportunities:
            result = self.executor.execute_trade(opp, paper_trading=True)

            if result['success']:
                executed_count += 1
                if executed_count % 50 == 0:
                    print(f"   Executed {executed_count} trades... Capital: ${self.executor.capital:,.2f}")
            else:
                failed_count += 1

        print(f"✅ Successfully executed {executed_count} trades")
        print(f"   Failed trades: {failed_count} (confirmation timeouts/price movements)\n")

        # Step 4: Calculate performance
        print("📈 Step 4: Calculating performance metrics...")
        performance = self.executor.get_performance_summary()
        performance['sharpe_ratio'] = self._calculate_sharpe_ratio()
        performance['max_drawdown'] = self._calculate_max_drawdown()
        performance['calmar_ratio'] = (
            performance['total_return_pct'] / abs(performance['max_drawdown'])
            if performance['max_drawdown'] != 0 else 0
        )
        performance['failed_trades'] = failed_count

        self.results = performance
        print("✅ Performance analysis complete\n")

        # Display results
        self._display_results()

        return performance

    def _show_opportunity_breakdown(self, opportunities: List):
        """Show breakdown of opportunities by pair and exchange"""
        print("\n📋 Opportunity Breakdown:")

        # Count by pair
        pair_counts = {}
        for opp in opportunities:
            pair_counts[opp.pair] = pair_counts.get(opp.pair, 0) + 1

        print("\n  By Trading Pair:")
        for pair, count in sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {pair}: {count} opportunities")

        # Count by exchange combination
        exchange_counts = {}
        for opp in opportunities:
            combo = f"{opp.buy_exchange} -> {opp.sell_exchange}"
            exchange_counts[combo] = exchange_counts.get(combo, 0) + 1

        print("\n  Top Exchange Routes:")
        for combo, count in sorted(exchange_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {combo}: {count} opportunities")

        # XMR opportunities
        xmr_opps = [o for o in opportunities if 'XMR' in o.pair]
        print(f"\n  🔒 Monero (XMR) opportunities: {len(xmr_opps)} ({len(xmr_opps)/len(opportunities)*100:.1f}%)")

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        if not self.executor.trades:
            return 0.0

        returns = [t['profit_pct'] / 100 for t in self.executor.trades if t['success']]

        if len(returns) < 2:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return / std_return) * np.sqrt(len(returns))
        return sharpe

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.executor.trades:
            return 0.0

        capital_history = [self.initial_capital]
        current_capital = self.initial_capital

        for trade in self.executor.trades:
            if trade['success']:
                current_capital = trade['capital_after']
                capital_history.append(current_capital)

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
        """Display formatted results"""
        perf = self.results

        print("=" * 70)
        print("PRIVACY COIN ARBITRAGE RESULTS")
        print("=" * 70)
        print(f"Initial Capital:        ${perf['initial_capital']:,.2f}")
        print(f"Final Capital:          ${perf['final_capital']:,.2f}")
        print(f"Total Profit:           ${perf['total_profit_usd']:,.2f}")
        print(f"Total Return:           {perf['total_return_pct']:.2f}%")
        print("-" * 70)
        print(f"Total Trades:           {perf['total_trades']}")
        print(f"Failed Trades:          {perf['failed_trades']}")
        print(f"Win Rate:               {perf['win_rate']:.2f}%")
        print(f"Avg Profit/Trade:       ${perf['avg_profit_per_trade']:.2f}")
        print("-" * 70)
        print(f"Total Fees Paid:        ${perf['total_fees_paid']:,.2f}")
        print(f"Net Profit After Fees:  ${perf['net_profit_after_fees']:,.2f}")
        print("-" * 70)
        print(f"🔒 Monero (XMR) Trades:  {perf['xmr_trades']} ({perf['xmr_percentage']:.1f}%)")
        print(f"⏱️  Avg Confirmation:     {perf['avg_confirmation_time']:.1f} minutes")
        print(f"⚠️  Avg Risk Score:       {perf['avg_risk_score']:.2f}/1.0")
        print("-" * 70)
        print(f"Sharpe Ratio:           {perf['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:           {perf['max_drawdown']:.2f}%")
        print(f"Calmar Ratio:           {perf['calmar_ratio']:.2f}")
        print("=" * 70)

        # Privacy coin info
        print("\n🔒 Privacy Coin Information:")
        coin_info = get_privacy_coin_info()
        print(f"\n  Monero (XMR): {coin_info['XMR']['notes']}")
        print(f"  Privacy Level: {coin_info['XMR']['privacy']}")
        print(f"  Network Fees: {coin_info['XMR']['fee']}")

    def _empty_results(self) -> Dict:
        """Return empty results"""
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.initial_capital,
            'total_trades': 0,
            'failed_trades': 0,
            'total_profit_usd': 0.0,
            'total_return_pct': 0.0,
            'win_rate': 0.0,
            'avg_profit_per_trade': 0.0,
            'total_fees_paid': 0.0,
            'net_profit_after_fees': 0.0,
            'xmr_trades': 0,
            'xmr_percentage': 0.0,
            'avg_confirmation_time': 0.0,
            'avg_risk_score': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'calmar_ratio': 0.0,
            'trades': []
        }

    def save_results(self, output_dir: str = "./results_privacy"):
        """Save backtest results"""
        if not self.results:
            print("No results to save")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save summary
        summary_file = output_path / f"privacy_backtest_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("PRIVACY COIN ARBITRAGE BACKTEST SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            for key, value in self.results.items():
                if key != 'trades':
                    f.write(f"{key}: {value}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("PRIVACY COIN INFORMATION\n")
            f.write("=" * 70 + "\n\n")

            coin_info = get_privacy_coin_info()
            for coin, info in coin_info.items():
                f.write(f"\n{coin} - {info['name']}:\n")
                for k, v in info.items():
                    if k != 'name':
                        f.write(f"  {k}: {v}\n")

        # Save trade history
        if self.results['trades']:
            trades_df = pd.DataFrame(self.results['trades'])
            trades_file = output_path / f"privacy_trade_history_{timestamp}.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"✅ Saved trade history to: {trades_file}")

        print(f"✅ Saved summary to: {summary_file}")

    def plot_performance(self, output_dir: str = "./results_privacy"):
        """Plot performance charts"""
        if not self.executor.trades:
            print("No trades to plot")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamps = []
        capital_values = []
        current_capital = self.initial_capital

        for trade in self.executor.trades:
            if trade['success']:
                timestamps.append(trade['timestamp'])
                current_capital = trade['capital_after']
                capital_values.append(current_capital)

        if not timestamps:
            return

        fig, axes = plt.subplots(3, 1, figsize=(14, 10))

        # Equity curve
        axes[0].plot(timestamps, capital_values, linewidth=2, color='#2E86AB')
        axes[0].axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5)
        axes[0].set_title('Equity Curve - Privacy Coin Arbitrage', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Capital (USD)', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylim(bottom=0)

        # Trade profits
        trade_profits = [t['profit_usd'] for t in self.executor.trades if t['success']]
        colors = ['green' if p > 0 else 'red' for p in trade_profits]
        axes[1].bar(range(len(trade_profits)), trade_profits, color=colors, alpha=0.6)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1].set_title('Trade Profits', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Trade Number', fontsize=12)
        axes[1].set_ylabel('Profit (USD)', fontsize=12)
        axes[1].grid(True, alpha=0.3, axis='y')

        # Risk scores over time
        risk_scores = [t['risk_score'] for t in self.executor.trades if t['success']]
        axes[2].plot(range(len(risk_scores)), risk_scores, color='orange', alpha=0.7, linewidth=1)
        axes[2].axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Medium Risk')
        axes[2].axhline(y=0.7, color='darkred', linestyle='--', alpha=0.5, label='High Risk')
        axes[2].set_title('Trade Risk Scores', fontsize=14, fontweight='bold')
        axes[2].set_xlabel('Trade Number', fontsize=12)
        axes[2].set_ylabel('Risk Score', fontsize=12)
        axes[2].set_ylim([0, 1])
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()

        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_file = output_path / f"privacy_performance_{timestamp}.png"
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"✅ Saved performance chart to: {plot_file}")
        plt.close()


def main():
    """Main entry point for privacy coin backtesting"""

    # Configuration
    INITIAL_CAPITAL = 15000  # $15,000
    START_DATE = datetime(2025, 8, 1, tzinfo=timezone.utc)
    END_DATE = datetime(2025, 10, 31, 23, 59, tzinfo=timezone.utc)
    MIN_PROFIT_PCT = 0.8  # 0.8% minimum (higher spreads = more opportunities)
    MAX_TRADE_SIZE = 5000
    MIN_TRADE_SIZE = 100

    # Run backtest
    backtest = PrivacyCoinBacktest(
        initial_capital=INITIAL_CAPITAL,
        min_profit_pct=MIN_PROFIT_PCT,
        max_trade_size=MAX_TRADE_SIZE,
        min_trade_size=MIN_TRADE_SIZE
    )

    results = backtest.run(
        start_date=START_DATE,
        end_date=END_DATE,
        interval_minutes=10  # Check every 10 minutes
    )

    # Save results
    backtest.save_results()
    backtest.plot_performance()

    print("\n🎉 Privacy coin backtest complete!")
    print(f"\n💰 You could have turned ${INITIAL_CAPITAL:,} into ${results['final_capital']:,.2f}")
    print(f"   That's a {results['total_return_pct']:.2f}% return in 3 months!")
    print(f"\n🔒 {results['xmr_trades']} trades used Monero for maximum privacy")
    print(f"   Average confirmation time: {results['avg_confirmation_time']:.1f} minutes")


if __name__ == "__main__":
    main()
