#!/bin/bash
# Quick Start - Eleanor Platform Paper Trading
# Starts the Selenium scraper + AI decision engine + paper trading

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Eleanor Platform - Quick Start (Paper Trading)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run ./setup_ubuntu.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}[1/3]${NC} Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo -e "${GREEN}[2/3]${NC} Verifying dependencies..."
python3 -c "import selenium, sklearn, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Dependencies not installed!${NC}"
    echo -e "${YELLOW}Please run ./setup_ubuntu.sh first${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies verified${NC}"
echo

# Start paper trading
echo -e "${GREEN}[3/3]${NC} Starting paper trading..."
echo
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Initial Capital:    ${GREEN}\$15,000${NC}"
echo -e "  Trading Pairs:      ${GREEN}ETH/USDC, WBTC/USDC, ETH/USDT${NC}"
echo -e "  Scrape Interval:    ${GREEN}15 minutes${NC}"
echo -e "  Mode:               ${GREEN}Paper Trading (Safe)${NC}"
echo -e "  Headless Browser:   ${GREEN}Yes${NC}"
echo
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop trading${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

cd src/eleanor
python3 orchestrator/scrape_and_trade.py
