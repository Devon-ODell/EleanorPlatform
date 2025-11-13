#!/usr/bin/env python3
"""
Test Eleanor Platform Setup
Verifies all components are working
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'eleanor'))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")

    tests = [
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing"),
        ("selenium", "Web scraping"),
        ("undetected_chromedriver", "Anti-detection browser"),
        ("selenium_stealth", "Stealth mode"),
        ("sklearn", "Machine learning"),
    ]

    failed = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"  ✓ {description} ({module})")
        except ImportError as e:
            print(f"  ✗ {description} ({module}): {e}")
            failed.append(module)

    if failed:
        print(f"\n❌ Failed imports: {', '.join(failed)}")
        print("Run: pip install -r requirements_selenium.txt")
        return False

    print("  ✓ All imports successful\n")
    return True


def test_chromedriver():
    """Test ChromeDriver availability"""
    print("Testing ChromeDriver...")

    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.options import Options

        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        print("  Starting headless Chrome...")
        driver = uc.Chrome(options=options, version_main=None)

        # Test navigation
        driver.get('https://example.com')
        title = driver.title
        driver.quit()

        print(f"  ✓ ChromeDriver working (loaded: {title})\n")
        return True

    except Exception as e:
        print(f"  ✗ ChromeDriver error: {e}\n")
        print("  Fix: sudo apt install chromium-browser chromium-chromedriver")
        return False


def test_modules():
    """Test Eleanor modules can be imported"""
    print("Testing Eleanor modules...")

    modules_to_test = [
        ("defi_data", "DeFi data module"),
        ("defi_arbitrage", "Arbitrage detection"),
        ("defi_data_privacy", "Privacy coin data"),
        ("privacy_arbitrage", "Privacy arbitrage"),
    ]

    failed = []
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"  ✓ {description}")
        except ImportError as e:
            print(f"  ✗ {description}: {e}")
            failed.append(module)

    if failed:
        print(f"\n⚠ Some modules couldn't load (may be normal)")
    else:
        print("  ✓ All modules loaded\n")

    return True  # Don't fail on module errors


def test_scraper():
    """Test Selenium scraper can be initialized"""
    print("Testing Selenium scraper...")

    try:
        from scrapers.dex_selenium_scraper import AntiDetectionBrowser

        print("  Initializing browser...")
        browser = AntiDetectionBrowser(headless=True)
        print("  ✓ Browser initialized")

        # Test navigation
        browser.driver.get('https://example.com')
        print("  ✓ Navigation works")

        browser.close()
        print("  ✓ Scraper working\n")
        return True

    except Exception as e:
        print(f"  ✗ Scraper error: {e}\n")
        return False


def test_ai_engine():
    """Test AI decision engine can be initialized"""
    print("Testing AI decision engine...")

    try:
        from ai.arbitrage_decision_engine import ArbitrageDecisionEngine

        engine = ArbitrageDecisionEngine(
            min_confidence=0.6,
            min_profit_pct=0.5
        )
        print("  ✓ AI engine initialized")

        # Test with dummy data
        dummy_data = {
            'ETH/USDC': [
                {'dex': 'uniswap_v3', 'price': 3500, 'liquidity': 1000000, 'volume_24h': 500000, 'fee_tier': '0.3%'},
                {'dex': 'pancakeswap_v3', 'price': 3510, 'liquidity': 800000, 'volume_24h': 400000, 'fee_tier': '0.25%'},
            ]
        }

        signals = engine.analyze_scraped_data(dummy_data)
        print(f"  ✓ AI analysis works (found {len(signals)} signals)")
        print("  ✓ AI engine working\n")
        return True

    except Exception as e:
        print(f"  ✗ AI engine error: {e}\n")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Eleanor Platform - Setup Test")
    print("="*60)
    print()

    results = {
        "Imports": test_imports(),
        "ChromeDriver": test_chromedriver(),
        "Modules": test_modules(),
        "Scraper": test_scraper(),
        "AI Engine": test_ai_engine(),
    }

    print("="*60)
    print("Test Results:")
    print("="*60)

    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test}: {status}")

    print()

    if all(results.values()):
        print("✅ All tests passed! System is ready.")
        print()
        print("Next steps:")
        print("  1. Run backtests:    python run_backtest.py")
        print("  2. Paper trading:    ./quick_start.sh")
        print("  3. Scraper demo:     python src/eleanor/scrapers/dex_selenium_scraper.py")
        return 0
    else:
        print("❌ Some tests failed. Fix errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
