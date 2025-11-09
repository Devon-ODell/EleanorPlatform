"""
Discreet DEX Data Scraper using Selenium
Targets: PancakeSwap V3, Uniswap V2/V3, Aerodrome, Fluid, Orca

Anti-detection features:
- Rotating user agents
- Random delays
- Headless mode with proper headers
- Proxy rotation support
- Browser fingerprint randomization
"""

import time
import random
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth

import undetected_chromedriver as uc


@dataclass
class DEXPrice:
    """Price data from a DEX"""
    timestamp: datetime
    dex: str
    pair: str
    price: float
    liquidity: float
    volume_24h: float
    fee_tier: Optional[str] = None


class AntiDetectionBrowser:
    """
    Browser instance with anti-detection measures
    Makes scraping look like human browsing
    """

    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self._setup_driver()

    def _get_random_user_agent(self) -> str:
        """Return random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        return random.choice(user_agents)

    def _setup_driver(self):
        """Setup Chrome driver with anti-detection"""
        options = uc.ChromeOptions()

        # Headless mode
        if self.headless:
            options.add_argument('--headless=new')

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent={self._get_random_user_agent()}')

        # Window size (mimic common resolutions)
        options.add_argument('--window-size=1920,1080')

        # Proxy if provided
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')

        # Additional anti-detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Initialize undetected chrome driver
        self.driver = uc.Chrome(options=options)

        # Execute stealth scripts
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

        # Override navigator.webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def scroll_randomly(self):
        """Random scrolling to mimic human browsing"""
        scroll_amount = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.human_delay(0.5, 1.5)

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


class UniswapV2Scraper:
    """Scraper for Uniswap V2"""

    BASE_URL = "https://app.uniswap.org/#/swap"
    DEX_NAME = "uniswap_v2"

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str) -> Optional[DEXPrice]:
        """
        Scrape price data for a token pair

        Args:
            token0: First token symbol (e.g., 'ETH')
            token1: Second token symbol (e.g., 'USDC')
        """
        try:
            # Navigate to swap page
            self.driver.get(self.BASE_URL)
            self.browser.human_delay(2, 4)

            # Wait for page load
            wait = WebDriverWait(self.driver, 10)

            # Select input token (token0)
            # This is a simplified example - actual implementation needs to handle
            # token selection via search and clicking
            input_token_selector = 'button[id="swap-currency-input"]'
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, input_token_selector)))

            # Enter amount (1.0 to get price)
            amount_input = self.driver.find_element(By.CSS_SELECTOR, 'input[inputmode="decimal"]')
            amount_input.clear()
            amount_input.send_keys('1.0')

            self.browser.human_delay(1, 2)

            # Extract price from output
            # Actual selectors depend on Uniswap's current DOM structure
            output_amount_selector = 'div[class*="output"] input'
            output_amount = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, output_amount_selector))
            )

            price = float(output_amount.get_attribute('value'))

            # Extract liquidity and volume (may need to navigate to info page)
            liquidity = self._get_pool_liquidity(token0, token1)
            volume_24h = self._get_24h_volume(token0, token1)

            return DEXPrice(
                timestamp=datetime.now(),
                dex=self.DEX_NAME,
                pair=f"{token0}/{token1}",
                price=price,
                liquidity=liquidity,
                volume_24h=volume_24h,
                fee_tier="0.3%"
            )

        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"Error scraping Uniswap V2 {token0}/{token1}: {e}")
            return None

    def _get_pool_liquidity(self, token0: str, token1: str) -> float:
        """
        Navigate to pool info page and extract liquidity
        This is a placeholder - actual implementation needed
        """
        # Would navigate to https://info.uniswap.org/pair/{pair_address}
        # and extract liquidity value
        return 0.0

    def _get_24h_volume(self, token0: str, token1: str) -> float:
        """Extract 24h volume"""
        # Similar to liquidity extraction
        return 0.0


class UniswapV3Scraper:
    """Scraper for Uniswap V3 (supports multiple fee tiers)"""

    BASE_URL = "https://app.uniswap.org/#/swap"
    INFO_URL = "https://info.uniswap.org/#/"
    DEX_NAME = "uniswap_v3"

    FEE_TIERS = ['0.01%', '0.05%', '0.3%', '1%']

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str, fee_tier: str = '0.3%') -> Optional[DEXPrice]:
        """
        Scrape Uniswap V3 pair with specific fee tier

        V3 has multiple pools per pair with different fee tiers
        """
        try:
            # Navigate to info page for specific pool
            pool_url = f"{self.INFO_URL}pools"
            self.driver.get(pool_url)
            self.browser.human_delay(2, 4)

            wait = WebDriverWait(self.driver, 10)

            # Search for pool
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]'))
            )
            search_input.send_keys(f"{token0}/{token1}")
            self.browser.human_delay(1, 2)

            # Find pool with matching fee tier
            pool_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr[class*="pool-row"]')

            for row in pool_rows:
                if fee_tier in row.text:
                    # Extract data from row
                    cells = row.find_elements(By.TAG_NAME, 'td')

                    # Parse pool data (example structure)
                    liquidity = self._parse_liquidity(cells[2].text)
                    volume_24h = self._parse_volume(cells[3].text)

                    # Get price by clicking into pool
                    row.click()
                    self.browser.human_delay(1, 2)

                    price = self._extract_pool_price()

                    return DEXPrice(
                        timestamp=datetime.now(),
                        dex=self.DEX_NAME,
                        pair=f"{token0}/{token1}",
                        price=price,
                        liquidity=liquidity,
                        volume_24h=volume_24h,
                        fee_tier=fee_tier
                    )

            return None

        except Exception as e:
            logging.error(f"Error scraping Uniswap V3 {token0}/{token1}: {e}")
            return None

    def _parse_liquidity(self, text: str) -> float:
        """Parse liquidity text like '$1.2M' to float"""
        text = text.replace('$', '').replace(',', '')
        if 'M' in text:
            return float(text.replace('M', '')) * 1_000_000
        elif 'K' in text:
            return float(text.replace('K', '')) * 1_000
        elif 'B' in text:
            return float(text.replace('B', '')) * 1_000_000_000
        return float(text)

    def _parse_volume(self, text: str) -> float:
        """Parse volume text"""
        return self._parse_liquidity(text)

    def _extract_pool_price(self) -> float:
        """Extract current pool price from pool detail page"""
        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, 'div[class*="price"]')
            price_text = price_element.text
            return float(price_text.split()[0].replace(',', ''))
        except:
            return 0.0


class PancakeSwapV3Scraper:
    """Scraper for PancakeSwap V3 (BSC and other chains)"""

    BASE_URL = "https://pancakeswap.finance/swap"
    INFO_URL = "https://pancakeswap.finance/info/v3"
    DEX_NAME = "pancakeswap_v3"

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str, chain: str = 'bsc') -> Optional[DEXPrice]:
        """
        Scrape PancakeSwap V3 pair

        Args:
            token0: First token
            token1: Second token
            chain: 'bsc', 'ethereum', 'arbitrum', etc.
        """
        try:
            # Navigate to swap page
            self.driver.get(self.BASE_URL)
            self.browser.human_delay(2, 4)

            # Switch to correct chain if needed
            self._switch_chain(chain)

            wait = WebDriverWait(self.driver, 10)

            # Click token selector
            token_selector_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id*="swap-currency"]'))
            )
            token_selector_btn.click()
            self.browser.human_delay(0.5, 1)

            # Search and select token
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]'))
            )
            search_input.send_keys(token0)
            self.browser.human_delay(1, 2)

            # Click first result
            first_result = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class*="token-item"]'))
            )
            first_result.click()
            self.browser.human_delay(1, 2)

            # Enter amount
            amount_input = self.driver.find_element(By.CSS_SELECTOR, 'input[inputmode="decimal"]')
            amount_input.send_keys('1.0')
            self.browser.human_delay(2, 3)

            # Extract price from output
            output_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="swap-output"]'))
            )
            price = self._extract_price_from_output(output_element)

            # Get pool info from info page
            liquidity, volume = self._get_pool_info(token0, token1, chain)

            return DEXPrice(
                timestamp=datetime.now(),
                dex=self.DEX_NAME,
                pair=f"{token0}/{token1}",
                price=price,
                liquidity=liquidity,
                volume_24h=volume,
                fee_tier="0.25%"  # PCS V3 default
            )

        except Exception as e:
            logging.error(f"Error scraping PancakeSwap V3: {e}")
            return None

    def _switch_chain(self, chain: str):
        """Switch to specified blockchain"""
        # Click network selector
        # Select chain from dropdown
        # Wait for switch to complete
        pass

    def _extract_price_from_output(self, element) -> float:
        """Extract price from output element"""
        try:
            price_text = element.text
            return float(price_text.split()[0].replace(',', ''))
        except:
            return 0.0

    def _get_pool_info(self, token0: str, token1: str, chain: str) -> tuple:
        """Navigate to info page and get liquidity/volume"""
        # Navigate to info page
        # Extract pool data
        return (0.0, 0.0)


class AerodromeScraper:
    """Scraper for Aerodrome (Base chain DEX)"""

    BASE_URL = "https://aerodrome.finance/swap"
    DEX_NAME = "aerodrome"

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str) -> Optional[DEXPrice]:
        """Scrape Aerodrome pair (Base chain)"""
        try:
            self.driver.get(self.BASE_URL)
            self.browser.human_delay(2, 4)

            wait = WebDriverWait(self.driver, 10)

            # Aerodrome has similar UI to other DEXs
            # Select tokens and get price

            # Implementation similar to Uniswap/PancakeSwap
            # Specific to Aerodrome's DOM structure

            return DEXPrice(
                timestamp=datetime.now(),
                dex=self.DEX_NAME,
                pair=f"{token0}/{token1}",
                price=0.0,  # Extract from page
                liquidity=0.0,
                volume_24h=0.0
            )

        except Exception as e:
            logging.error(f"Error scraping Aerodrome: {e}")
            return None


class FluidScraper:
    """Scraper for Fluid DEX"""

    BASE_URL = "https://fluid.instadapp.io/"
    DEX_NAME = "fluid"

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str) -> Optional[DEXPrice]:
        """Scrape Fluid pair"""
        try:
            self.driver.get(self.BASE_URL)
            self.browser.human_delay(2, 4)

            # Fluid-specific scraping logic
            # Similar pattern to other DEXs

            return DEXPrice(
                timestamp=datetime.now(),
                dex=self.DEX_NAME,
                pair=f"{token0}/{token1}",
                price=0.0,
                liquidity=0.0,
                volume_24h=0.0
            )

        except Exception as e:
            logging.error(f"Error scraping Fluid: {e}")
            return None


class OrcaScraper:
    """Scraper for Orca (Solana DEX)"""

    BASE_URL = "https://www.orca.so/"
    DEX_NAME = "orca"

    def __init__(self, browser: AntiDetectionBrowser):
        self.browser = browser
        self.driver = browser.driver

    def scrape_pair(self, token0: str, token1: str) -> Optional[DEXPrice]:
        """Scrape Orca pair (Solana)"""
        try:
            self.driver.get(self.BASE_URL)
            self.browser.human_delay(2, 4)

            wait = WebDriverWait(self.driver, 10)

            # Click "Trade" or "Swap"
            trade_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Swap')]"))
            )
            trade_btn.click()
            self.browser.human_delay(2, 3)

            # Select tokens
            # Orca has different UI than EVM DEXs

            # Extract price

            return DEXPrice(
                timestamp=datetime.now(),
                dex=self.DEX_NAME,
                pair=f"{token0}/{token1}",
                price=0.0,
                liquidity=0.0,
                volume_24h=0.0
            )

        except Exception as e:
            logging.error(f"Error scraping Orca: {e}")
            return None


class MultiDEXScraper:
    """
    Coordinates scraping across multiple DEXs
    Implements rotation and anti-detection
    """

    def __init__(self,
                 headless: bool = True,
                 use_proxy: bool = False,
                 proxy_list: Optional[List[str]] = None):
        self.headless = headless
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0

        # Initialize browser
        self.browser = None
        self._init_browser()

        # Initialize scrapers
        self.scrapers = {
            'uniswap_v2': UniswapV2Scraper(self.browser),
            'uniswap_v3': UniswapV3Scraper(self.browser),
            'pancakeswap_v3': PancakeSwapV3Scraper(self.browser),
            'aerodrome': AerodromeScraper(self.browser),
            'fluid': FluidScraper(self.browser),
            'orca': OrcaScraper(self.browser),
        }

    def _init_browser(self):
        """Initialize or reinitialize browser with new proxy"""
        if self.browser:
            self.browser.close()

        proxy = None
        if self.use_proxy and self.proxy_list:
            proxy = self.proxy_list[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)

        self.browser = AntiDetectionBrowser(
            headless=self.headless,
            proxy=proxy
        )

    def scrape_all(self, pairs: List[tuple]) -> Dict[str, List[DEXPrice]]:
        """
        Scrape all DEXs for given pairs

        Args:
            pairs: List of (token0, token1) tuples

        Returns:
            Dictionary mapping pair to list of prices from different DEXs
        """
        results = {}

        for token0, token1 in pairs:
            pair_key = f"{token0}/{token1}"
            results[pair_key] = []

            logging.info(f"Scraping {pair_key}...")

            # Scrape each DEX
            for dex_name, scraper in self.scrapers.items():
                try:
                    # Random delay between DEXs
                    self.browser.human_delay(5, 10)

                    # Scrape
                    price_data = scraper.scrape_pair(token0, token1)

                    if price_data:
                        results[pair_key].append(price_data)
                        logging.info(f"  ✓ {dex_name}: {price_data.price}")
                    else:
                        logging.warning(f"  ✗ {dex_name}: No data")

                    # Random scrolling to mimic human
                    if random.random() < 0.3:
                        self.browser.scroll_randomly()

                except Exception as e:
                    logging.error(f"  ✗ {dex_name}: Error - {e}")

            # Longer delay between pairs
            if len(pairs) > 1:
                self.browser.human_delay(10, 20)

        return results

    def rotate_proxy(self):
        """Rotate to next proxy and reinit browser"""
        if self.use_proxy:
            self._init_browser()
            # Reinitialize all scrapers with new browser
            for dex_name in self.scrapers:
                self.scrapers[dex_name].browser = self.browser
                self.scrapers[dex_name].driver = self.browser.driver

    def close(self):
        """Clean up"""
        if self.browser:
            self.browser.close()


def main():
    """Example usage"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Define pairs to scrape
    pairs = [
        ('ETH', 'USDC'),
        ('WBTC', 'USDC'),
        ('MATIC', 'USDC'),
    ]

    # Optional proxy list (for extra privacy)
    proxies = [
        # 'http://proxy1.example.com:8080',
        # 'http://proxy2.example.com:8080',
    ]

    # Initialize scraper
    scraper = MultiDEXScraper(
        headless=True,
        use_proxy=False,  # Set to True if using proxies
        proxy_list=proxies
    )

    try:
        # Scrape all DEXs
        results = scraper.scrape_all(pairs)

        # Print results
        print("\n" + "="*70)
        print("SCRAPED PRICES")
        print("="*70)

        for pair, prices in results.items():
            print(f"\n{pair}:")
            for price_data in prices:
                print(f"  {price_data.dex}: ${price_data.price:.4f} "
                      f"(Liquidity: ${price_data.liquidity:,.0f}, "
                      f"Volume: ${price_data.volume_24h:,.0f})")

        # Save to JSON
        output = {}
        for pair, prices in results.items():
            output[pair] = [
                {
                    'dex': p.dex,
                    'price': p.price,
                    'liquidity': p.liquidity,
                    'volume_24h': p.volume_24h,
                    'timestamp': p.timestamp.isoformat()
                }
                for p in prices
            ]

        with open('dex_prices.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✅ Saved to dex_prices.json")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
