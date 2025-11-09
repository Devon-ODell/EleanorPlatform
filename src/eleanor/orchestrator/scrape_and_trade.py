"""
Main Orchestrator: Selenium Scraping → AI Analysis → Arbitrage Execution

Connects all components:
1. Selenium DEX scraper (discreet data gathering)
2. AI decision engine (signal generation)
3. Arbitrage execution (trade execution)

Runs continuously or on schedule
"""

import time
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.dex_selenium_scraper import MultiDEXScraper
from ai.arbitrage_decision_engine import ArbitrageDecisionEngine, ArbitrageSignal
from defi_arbitrage import ArbitrageExecutor
from monitoring.prometheus_metrics import get_metrics, start_metrics_server


class ArbitrageOrchestrator:
    """
    Main orchestrator for automated arbitrage trading
    """

    def __init__(self,
                 initial_capital: float = 15000,
                 scrape_interval_minutes: int = 15,
                 use_headless: bool = True,
                 use_proxy: bool = False,
                 proxy_list: list = None,
                 paper_trading: bool = True,
                 enable_metrics: bool = True,
                 metrics_port: int = 8000):
        """
        Initialize orchestrator

        Args:
            initial_capital: Starting capital
            scrape_interval_minutes: How often to scrape DEXs
            use_headless: Run browser in headless mode
            use_proxy: Use proxy rotation
            proxy_list: List of proxy servers
            paper_trading: If True, simulate trades; if False, execute real trades
            enable_metrics: Enable Prometheus metrics (default True)
            metrics_port: Port for Prometheus metrics endpoint (default 8000)
        """
        self.initial_capital = initial_capital
        self.scrape_interval = timedelta(minutes=scrape_interval_minutes)
        self.paper_trading = paper_trading
        self.start_time = datetime.now()

        # Initialize Prometheus metrics
        self.enable_metrics = enable_metrics
        if enable_metrics:
            logging.info(f"Initializing Prometheus metrics on port {metrics_port}...")
            start_metrics_server(port=metrics_port)
            self.metrics = get_metrics(port=metrics_port)
            self.metrics.update_capital(initial_capital)
        else:
            self.metrics = None

        # Initialize scraper
        logging.info("Initializing DEX scraper...")
        self.scraper = MultiDEXScraper(
            headless=use_headless,
            use_proxy=use_proxy,
            proxy_list=proxy_list or []
        )

        # Initialize AI decision engine
        logging.info("Initializing AI decision engine...")
        self.ai_engine = ArbitrageDecisionEngine(
            min_confidence=0.6,
            min_profit_pct=0.5,
            max_risk_score=0.6
        )

        # Initialize executor
        logging.info("Initializing arbitrage executor...")
        self.executor = ArbitrageExecutor(initial_capital_usd=initial_capital)

        # Tracking
        self.last_scrape_time = None
        self.scrape_count = 0
        self.trade_count = 0

        # Data storage
        self.data_dir = Path("./data/arbitrage")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run_single_cycle(self, pairs: list) -> dict:
        """
        Run one complete cycle:
        1. Scrape DEXs
        2. Analyze with AI
        3. Execute trades

        Args:
            pairs: List of (token0, token1) tuples to trade

        Returns:
            Dictionary with cycle results
        """
        cycle_start = datetime.now()
        logging.info(f"\n{'='*80}")
        logging.info(f"CYCLE #{self.scrape_count + 1} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"{'='*80}\n")

        results = {
            'cycle_number': self.scrape_count + 1,
            'timestamp': cycle_start,
            'scraped_pairs': 0,
            'signals_generated': 0,
            'trades_executed': 0,
            'trades_successful': 0,
            'total_profit': 0.0,
            'current_capital': self.executor.capital,
            'signals': []
        }

        try:
            # Step 1: Scrape DEXs
            logging.info("STEP 1: Scraping DEXs...")
            scrape_start = datetime.now()
            scraped_data = self.scraper.scrape_all(pairs)
            scrape_duration = (datetime.now() - scrape_start).total_seconds()
            results['scraped_pairs'] = len(scraped_data)

            # Record scraping metrics
            if self.metrics:
                self.metrics.record_scrape(scrape_duration, len(scraped_data))
                self.metrics.update_last_scrape_time(datetime.now().timestamp())
                # Count DEX price points
                for pair, prices in scraped_data.items():
                    for p in prices:
                        self.metrics.record_dex_price(p.dex)

            # Save scraped data
            self._save_scraped_data(scraped_data)

            # Log scraping results
            for pair, prices in scraped_data.items():
                if prices:
                    prices_str = ", ".join([f"{p.dex}: ${p.price:.4f}" for p in prices])
                    logging.info(f"  {pair}: {prices_str}")

            # Step 2: AI Analysis
            logging.info("\nSTEP 2: AI Analysis...")

            # Convert to format expected by AI engine
            scraped_dict = {}
            for pair, prices in scraped_data.items():
                scraped_dict[pair] = [
                    {
                        'dex': p.dex,
                        'price': p.price,
                        'liquidity': p.liquidity,
                        'volume_24h': p.volume_24h,
                        'fee_tier': p.fee_tier
                    }
                    for p in prices
                ]

            signals = self.ai_engine.analyze_scraped_data(scraped_dict)
            results['signals_generated'] = len(signals)

            # Record signal metrics
            if self.metrics:
                for signal in signals:
                    self.metrics.record_signal(
                        priority=signal.execution_priority,
                        confidence=signal.confidence_score,
                        risk=signal.risk_score,
                        buy_dex=signal.buy_dex,
                        sell_dex=signal.sell_dex
                    )

            # Log signals
            if signals:
                logging.info(f"\n  ✅ Generated {len(signals)} arbitrage signals:")
                for i, signal in enumerate(signals[:5], 1):  # Show top 5
                    logging.info(f"    #{i} {signal.pair}: "
                               f"{signal.buy_dex} → {signal.sell_dex} | "
                               f"Profit: ${signal.expected_profit_usd:.2f} ({signal.net_profit_pct:.2f}%) | "
                               f"Confidence: {signal.confidence_score:.1%} | "
                               f"Priority: {signal.execution_priority}")

                # Save signals
                results['signals'] = self._format_signals_for_storage(signals)
            else:
                logging.info("  ℹ️ No profitable opportunities found")

            # Step 3: Execute Trades
            if signals:
                logging.info("\nSTEP 3: Executing Trades...")

                executed = 0
                successful = 0
                total_profit = 0.0

                # Execute top signals (based on priority and expected profit)
                high_priority = [s for s in signals if s.execution_priority == 'high']
                medium_priority = [s for s in signals if s.execution_priority == 'medium']

                # Execute high priority first
                for signal in high_priority[:3]:  # Top 3 high priority
                    result = self._execute_signal(signal)
                    executed += 1

                    if result['success']:
                        successful += 1
                        total_profit += result.get('profit_usd', 0)

                # Execute medium priority if capital available
                if self.executor.capital > self.initial_capital * 0.5:  # At least 50% capital left
                    for signal in medium_priority[:2]:  # Top 2 medium priority
                        result = self._execute_signal(signal)
                        executed += 1

                        if result['success']:
                            successful += 1
                            total_profit += result.get('profit_usd', 0)

                results['trades_executed'] = executed
                results['trades_successful'] = successful
                results['total_profit'] = total_profit
                results['current_capital'] = self.executor.capital

                logging.info(f"\n  Executed: {executed} trades")
                logging.info(f"  Successful: {successful} trades")
                logging.info(f"  Total Profit: ${total_profit:.2f}")
                logging.info(f"  Current Capital: ${self.executor.capital:,.2f}")

            # Update counters
            self.scrape_count += 1
            self.trade_count += results['trades_executed']
            self.last_scrape_time = cycle_start

            # Update performance metrics
            if self.metrics:
                performance = self.executor.get_performance_summary()
                self.metrics.update_capital(self.executor.capital)
                self.metrics.update_performance(
                    win_rate=performance.get('win_rate', 0) / 100.0,
                    total_return_pct=performance.get('total_return_pct', 0),
                    sharpe_ratio=performance.get('sharpe_ratio')
                )

            # Save cycle results
            self._save_cycle_results(results)

        except Exception as e:
            logging.error(f"Error in cycle: {e}", exc_info=True)
            results['error'] = str(e)

            # Record error metric
            if self.metrics:
                self.metrics.record_error('cycle_error')

        finally:
            cycle_duration = (datetime.now() - cycle_start).total_seconds()

            # Record cycle metrics
            if self.metrics:
                self.metrics.record_cycle(cycle_duration)
                uptime = (datetime.now() - self.start_time).total_seconds()
                self.metrics.update_uptime(uptime)

            logging.info(f"\nCycle completed in {cycle_duration:.1f}s")

        return results

    def _execute_signal(self, signal: ArbitrageSignal) -> dict:
        """
        Execute a single arbitrage signal

        Convert ArbitrageSignal to format expected by executor
        """
        logging.info(f"\n  Executing: {signal.pair} ({signal.buy_dex} → {signal.sell_dex})")
        logging.info(f"    Expected profit: ${signal.expected_profit_usd:.2f} ({signal.net_profit_pct:.2f}%)")
        logging.info(f"    Size: ${signal.recommended_size_usd:.0f}")

        # Create opportunity object for executor
        # This is a simplified version - in production, you'd convert the signal properly
        from dataclasses import dataclass as dc

        @dc
        class Opportunity:
            pair: str
            buy_exchange: str
            sell_exchange: str
            buy_price: float
            sell_price: float
            optimal_size_usd: float
            expected_profit_usd: float
            net_profit_pct: float

        opportunity = Opportunity(
            pair=signal.pair,
            buy_exchange=signal.buy_dex,
            sell_exchange=signal.sell_dex,
            buy_price=signal.buy_price,
            sell_price=signal.sell_price,
            optimal_size_usd=signal.recommended_size_usd,
            expected_profit_usd=signal.expected_profit_usd,
            net_profit_pct=signal.net_profit_pct
        )

        # Execute trade
        result = self.executor.execute_trade(opportunity, paper_trading=self.paper_trading)

        # Record outcome in AI engine for learning
        if result['success']:
            actual_profit = result.get('profit_usd', 0)
            self.ai_engine.record_trade_outcome(signal, actual_profit, True)
            logging.info(f"    ✅ Trade successful! Profit: ${actual_profit:.2f}")

            # Record successful trade metrics
            if self.metrics:
                self.metrics.record_trade(
                    success=True,
                    priority=signal.execution_priority,
                    profit_usd=actual_profit,
                    size_usd=signal.recommended_size_usd,
                    profit_pct=signal.net_profit_pct
                )
        else:
            self.ai_engine.record_trade_outcome(signal, 0, False)
            logging.info(f"    ❌ Trade failed: {result.get('reason', 'Unknown')}")

            # Record failed trade metrics
            if self.metrics:
                self.metrics.record_trade(
                    success=False,
                    priority=signal.execution_priority,
                    profit_usd=0,
                    size_usd=signal.recommended_size_usd,
                    profit_pct=0
                )
                self.metrics.record_error('trade_error')

        return result

    def run_continuous(self,
                      pairs: list,
                      max_cycles: int = None,
                      max_duration_hours: int = None):
        """
        Run continuously until stopped

        Args:
            pairs: Trading pairs to monitor
            max_cycles: Maximum number of cycles (None = infinite)
            max_duration_hours: Maximum duration in hours (None = infinite)
        """
        start_time = datetime.now()
        cycles_run = 0

        logging.info("="*80)
        logging.info("STARTING CONTINUOUS ARBITRAGE TRADING")
        logging.info("="*80)
        logging.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logging.info(f"Scrape Interval: {self.scrape_interval.total_seconds() / 60:.0f} minutes")
        logging.info(f"Trading Pairs: {len(pairs)}")
        logging.info(f"Paper Trading: {self.paper_trading}")
        logging.info(f"Max Cycles: {max_cycles or 'Unlimited'}")
        logging.info(f"Max Duration: {max_duration_hours or 'Unlimited'} hours")
        logging.info("="*80)

        try:
            while True:
                # Check exit conditions
                if max_cycles and cycles_run >= max_cycles:
                    logging.info(f"\nReached maximum cycles ({max_cycles})")
                    break

                if max_duration_hours:
                    elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
                    if elapsed_hours >= max_duration_hours:
                        logging.info(f"\nReached maximum duration ({max_duration_hours}h)")
                        break

                # Run cycle
                results = self.run_single_cycle(pairs)
                cycles_run += 1

                # Retrain AI models periodically (every 100 cycles)
                if cycles_run % 100 == 0:
                    logging.info("\nRetraining AI models...")
                    self.ai_engine.retrain_models()

                # Rotate proxy periodically (every 10 cycles)
                if cycles_run % 10 == 0 and self.scraper.use_proxy:
                    logging.info("\nRotating proxy...")
                    self.scraper.rotate_proxy()

                # Wait until next scrape interval
                next_scrape = self.last_scrape_time + self.scrape_interval
                wait_seconds = (next_scrape - datetime.now()).total_seconds()

                if wait_seconds > 0:
                    logging.info(f"\nWaiting {wait_seconds / 60:.1f} minutes until next cycle...")
                    time.sleep(wait_seconds)

        except KeyboardInterrupt:
            logging.info("\n\nStopping (Ctrl+C received)...")

        finally:
            self._cleanup()
            self._print_final_summary(start_time)

    def _cleanup(self):
        """Clean up resources"""
        logging.info("\nCleaning up...")
        if self.scraper:
            self.scraper.close()

    def _print_final_summary(self, start_time: datetime):
        """Print final trading summary"""
        duration = datetime.now() - start_time
        performance = self.executor.get_performance_summary()

        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Duration: {duration}")
        print(f"Cycles Run: {self.scrape_count}")
        print(f"Total Trades: {self.trade_count}")
        print("-"*80)
        print(f"Initial Capital: ${performance['initial_capital']:,.2f}")
        print(f"Final Capital:   ${performance['final_capital']:,.2f}")
        print(f"Total Profit:    ${performance['total_profit_usd']:,.2f}")
        print(f"Return:          {performance['total_return_pct']:.2f}%")
        print(f"Win Rate:        {performance['win_rate']:.1f}%")
        print("="*80)

    def _save_scraped_data(self, data: dict):
        """Save scraped data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"scraped_{timestamp}.json"

        # Convert to serializable format
        serializable_data = {}
        for pair, prices in data.items():
            serializable_data[pair] = [
                {
                    'dex': p.dex,
                    'price': p.price,
                    'liquidity': p.liquidity,
                    'volume_24h': p.volume_24h,
                    'timestamp': p.timestamp.isoformat()
                }
                for p in prices
            ]

        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2)

    def _format_signals_for_storage(self, signals: list) -> list:
        """Format signals for JSON storage"""
        return [
            {
                'pair': s.pair,
                'buy_dex': s.buy_dex,
                'sell_dex': s.sell_dex,
                'net_profit_pct': s.net_profit_pct,
                'expected_profit_usd': s.expected_profit_usd,
                'confidence': s.confidence_score,
                'risk': s.risk_score,
                'priority': s.execution_priority,
                'reasoning': s.reasoning
            }
            for s in signals
        ]

    def _save_cycle_results(self, results: dict):
        """Save cycle results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"cycle_{timestamp}.json"

        # Make datetime serializable
        results_copy = results.copy()
        results_copy['timestamp'] = results_copy['timestamp'].isoformat()

        with open(filename, 'w') as f:
            json.dump(results_copy, f, indent=2)


def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('arbitrage_bot.log'),
            logging.StreamHandler()
        ]
    )

    # Define trading pairs
    pairs = [
        ('ETH', 'USDC'),
        ('WBTC', 'USDC'),
        ('ETH', 'USDT'),
    ]

    # Optional: Proxy list for extra privacy
    proxies = [
        # Add your proxy servers here
        # 'http://proxy1.example.com:8080',
    ]

    # Initialize orchestrator
    orchestrator = ArbitrageOrchestrator(
        initial_capital=15000,
        scrape_interval_minutes=15,  # Scrape every 15 minutes
        use_headless=True,
        use_proxy=False,  # Set to True if using proxies
        proxy_list=proxies,
        paper_trading=True  # Start with paper trading!
    )

    # Run continuously
    orchestrator.run_continuous(
        pairs=pairs,
        max_cycles=None,  # Run indefinitely
        max_duration_hours=24  # Or set time limit
    )


if __name__ == "__main__":
    main()
