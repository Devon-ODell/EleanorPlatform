#!/bin/bash
# Eleanor Platform - Complete Setup Script for Ubuntu
# Makes the repo "drop and run" ready

set -e  # Exit on error

echo "=========================================="
echo "Eleanor Platform - Ubuntu Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo -e "${RED}Error: This script requires Ubuntu/Debian (apt package manager)${NC}"
    exit 1
fi

echo -e "${GREEN}[1/8]${NC} Updating system packages..."
sudo apt update

echo -e "${GREEN}[2/8]${NC} Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    chromium-browser \
    chromium-chromedriver \
    git \
    curl \
    wget

echo -e "${GREEN}[3/8]${NC} Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ Created virtual environment"
else
    echo "  ✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

echo -e "${GREEN}[4/8]${NC} Upgrading pip..."
pip install --upgrade pip

echo -e "${GREEN}[5/8]${NC} Installing Python dependencies..."
echo "  Installing core dependencies..."
pip install -q pandas numpy scipy matplotlib

echo "  Installing Selenium & anti-detection..."
pip install -q selenium undetected-chromedriver selenium-stealth

echo "  Installing ML libraries..."
pip install -q scikit-learn joblib

echo "  Installing web scraping tools..."
pip install -q beautifulsoup4 lxml requests

echo -e "${GREEN}[6/8]${NC} Creating necessary directories..."
mkdir -p src/eleanor/data/arbitrage
mkdir -p src/eleanor/results
mkdir -p src/eleanor/results_privacy
mkdir -p logs
echo "  ✓ Directories created"

echo -e "${GREEN}[7/8]${NC} Testing Selenium installation..."
python3 << 'PYTHON_TEST'
try:
    import selenium
    import undetected_chromedriver as uc
    from selenium_stealth import stealth
    print("  ✓ Selenium installed correctly")
except ImportError as e:
    print(f"  ✗ Error: {e}")
    exit(1)
PYTHON_TEST

echo -e "${GREEN}[8/8]${NC} Testing ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "  ✓ ChromeDriver found: $(chromedriver --version | head -1)"
else
    echo -e "${YELLOW}  ⚠ ChromeDriver not in PATH, but undetected-chromedriver will download it${NC}"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "What's installed:"
echo "  ✓ Python 3 with virtual environment"
echo "  ✓ Chromium browser + ChromeDriver"
echo "  ✓ Selenium + anti-detection tools"
echo "  ✓ Machine learning libraries"
echo "  ✓ All dependencies"
echo ""
echo "Quick Start:"
echo "  1. Activate environment:  source venv/bin/activate"
echo "  2. Run paper trading:     ./quick_start.sh"
echo "  3. Or run scraper test:   python test_setup.py"
echo ""
echo -e "${GREEN}Ready to trade!${NC}"
