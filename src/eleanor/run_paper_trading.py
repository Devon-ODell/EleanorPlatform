#!/usr/bin/env python3
"""
DeFi Arbitrage Paper Trading
Runs live paper trading simulation using real-time DEX data
"""
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from defi_data import DEXDataFetcher
from defi_arbitrage import ArbitrageDetector, ArbitrageExecutor


class PaperTradingSession:
    """Manages a paper trading session"""

    def __init__(self,
                 initial_capital: float = 15000,
                 min_profit_pct: float = 0.5,
                 check_interval_seconds: int = 30,
                 max_trade_size: float = 5000):
        """
        Initialize paper trading session

        Args:
            initial_capital: Starting capital in USD
            min_profit_pct: Minimum profit percentage to execute
            check_interval_seconds: How often to check for opportunities
            max_trade_size: Maximum trade size in USD
        """
        self.data_fetcher = DEXDataFetcher()
        self.detector = ArbitrageDetector(
            min_profit_pct=min_profit_pct,
            max_trade_size_usd=max_trade_size,
            min_trade_size_usd=100
        )
        self.executor = ArbitrageExecutor(initial_capital_usd=initial_capital)
        self.check_interval = check_interval_seconds
        self.running = False

    def start(self, duration_hours: int = 24):
        """
        Start paper trading session

        Args:
            duration_hours: How long to run (in hours), None for indefinite
        """
        print("=" * 70)
        print("DeFi ARBITRAGE PAPER TRADING")
        print("=" * 70)
        print(f"💰 Initial Capital: ${self.executor.capital:,.2f}")
        print(f"📊 Min Profit Threshold: {self.detector.min_profit_pct}%")
        print(f"⏱️  Check Interval: {self.check_interval}s")
        print(f"⏰ Duration: {duration_hours}h")
        print("=" * 70)
        print("\n🚀 Starting paper trading session...\n")

        self.running = True
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(hours=duration_hours) if duration_hours else None

        iteration = 0

        try:
            while self.running:
                iteration += 1
                current_time = datetime.now(timezone.utc)

                # Check if duration exceeded
                if end_time and current_time >= end_time:
                    print(f"\n⏰ Session duration reached ({duration_hours}h)")
                    break

                # Get current DEX prices (simulated with 5-min historical data)
                # In production, this would fetch live prices via APIs
                print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Iteration #{iteration}")
                print("📡 Fetching current DEX prices...")

                # Generate recent data (simulating live feed)
                lookback = current_time - timedelta(minutes=5)
                df = self.data_fetcher.generate_historical_data(
                    start_date=lookback,
                    end_date=current_time,
                    interval_minutes=5
                )

                # Detect opportunities
                opportunities = self.detector.find_opportunities(df)

                if opportunities:
                    print(f"✅ Found {len(opportunities)} arbitrage opportunities!")

                    # Execute the most profitable opportunity
                    best_opp = max(opportunities, key=lambda x: x.expected_profit_usd)

                    print(f"\n💎 BEST OPPORTUNITY:")
                    print(f"   Pair: {best_opp.pair}")
                    print(f"   Buy: {best_opp.buy_dex} @ ${best_opp.buy_price:.4f}")
                    print(f"   Sell: {best_opp.sell_dex} @ ${best_opp.sell_price:.4f}")
                    print(f"   Net Profit: {best_opp.net_profit_pct:.2f}% (${best_opp.expected_profit_usd:.2f})")
                    print(f"   Trade Size: ${best_opp.optimal_size_usd:.2f}")

                    # Execute trade
                    result = self.executor.execute_trade(best_opp, paper_trading=True)

                    if result['success']:
                        print(f"\n✅ TRADE EXECUTED!")
                        print(f"   Profit: ${result['profit_usd']:.2f}")
                        print(f"   Gas Fees: ${result['gas_paid']:.2f}")
                        print(f"   New Capital: ${result['capital_after']:,.2f}")
                    else:
                        print(f"\n❌ TRADE FAILED: {result['reason']}")
                else:
                    print("⚠️  No profitable opportunities found")

                # Display session stats
                perf = self.executor.get_performance_summary()
                print(f"\n📊 SESSION STATS:")
                print(f"   Total Trades: {perf['total_trades']}")
                print(f"   Current Capital: ${perf['final_capital']:,.2f}")
                print(f"   Total Profit: ${perf['total_profit_usd']:,.2f} ({perf['total_return_pct']:.2f}%)")
                print(f"   Win Rate: {perf['win_rate']:.1f}%")

                # Sleep until next check
                print(f"\n⏳ Waiting {self.check_interval}s until next check...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n\n⚠️  Stopping paper trading session (Ctrl+C received)...")
            self.running = False

        # Final summary
        self._print_final_summary()

    def stop(self):
        """Stop paper trading session"""
        self.running = False

    def _print_final_summary(self):
        """Print final session summary"""
        perf = self.executor.get_performance_summary()

        print("\n" + "=" * 70)
        print("PAPER TRADING SESSION SUMMARY")
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
        print("=" * 70)

        # Save trade history
        if perf['trades']:
            output_dir = Path("./data")
            output_dir.mkdir(exist_ok=True)

            import pandas as pd
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trades_df = pd.DataFrame(perf['trades'])
            trades_file = output_dir / f"paper_trading_{timestamp}.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"\n✅ Saved trade history to: {trades_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="DeFi Arbitrage Paper Trading")
    parser.add_argument("--capital", type=float, default=15000,
                       help="Initial capital in USD (default: 15000)")
    parser.add_argument("--min-profit", type=float, default=0.5,
                       help="Minimum profit percentage (default: 0.5)")
    parser.add_argument("--interval", type=int, default=30,
                       help="Check interval in seconds (default: 30)")
    parser.add_argument("--duration", type=int, default=24,
                       help="Duration in hours (default: 24)")
    parser.add_argument("--max-trade-size", type=float, default=5000,
                       help="Maximum trade size in USD (default: 5000)")

    args = parser.parse_args()

    # Start paper trading
    session = PaperTradingSession(
        initial_capital=args.capital,
        min_profit_pct=args.min_profit,
        check_interval_seconds=args.interval,
        max_trade_size=args.max_trade_size
    )

    session.start(duration_hours=args.duration)


if __name__ == "__main__":
    main()
