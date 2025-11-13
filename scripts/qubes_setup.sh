#!/bin/bash
# Eleanor Platform - Qubes OS Trading Qube Setup Script
# Run this inside your trading-qube after initial VM creation

set -e

echo "=========================================="
echo "Eleanor Platform - Qubes OS Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in Qubes
if [ ! -f /usr/bin/qvm-run ]; then
    echo -e "${YELLOW}Warning: This doesn't appear to be Qubes OS${NC}"
    echo "Continuing anyway..."
fi

# Verify VPN connection
echo -e "${GREEN}[1/8]${NC} Checking VPN connection..."
VPN_CHECK=$(curl -s https://am.i.mullvad.net/json 2>/dev/null || echo '{"mullvad_exit_ip":false}')
if echo "$VPN_CHECK" | grep -q '"mullvad_exit_ip":true'; then
    echo -e "${GREEN}✓ VPN connection verified (Mullvad)${NC}"
else
    echo -e "${RED}✗ WARNING: Not connected to Mullvad VPN!${NC}"
    echo "Please configure sys-vpn before continuing"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo -e "${GREEN}[2/8]${NC} Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo -e "${GREEN}[3/8]${NC} Installing dependencies..."
sudo apt install -y \
    python3 python3-pip python3-venv \
    git build-essential curl wget \
    tmux htop nethogs \
    software-properties-common

# Install Python 3.11 if not available
if ! command -v python3.11 &> /dev/null; then
    echo -e "${GREEN}[3/8]${NC} Installing Python 3.11..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Create trading directory
echo -e "${GREEN}[4/8]${NC} Setting up trading directory..."
mkdir -p ~/trading
cd ~/trading

# Clone repository if not exists
if [ ! -d "EleanorPlatform" ]; then
    echo -e "${GREEN}[5/8]${NC} Cloning Eleanor Platform..."
    git clone https://github.com/Devon-ODell/EleanorPlatform.git
    cd EleanorPlatform
    git checkout claude/hummingbot-defi-backtest-011CUvp5TPEuvpevnFLxgEAc
else
    echo -e "${YELLOW}Eleanor Platform already exists, updating...${NC}"
    cd EleanorPlatform
    git pull
fi

# Set up Python virtual environment
echo -e "${GREEN}[6/8]${NC} Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
echo -e "${GREEN}[7/8]${NC} Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p src/eleanor/results
mkdir -p src/eleanor/data
mkdir -p logs

# Create monitoring script
echo -e "${GREEN}[8/8]${NC} Setting up monitoring scripts..."

cat > ~/trading/check_vpn.sh << 'EOF'
#!/bin/bash
# VPN monitoring script

VPN_STATUS=$(curl -s https://am.i.mullvad.net/json 2>/dev/null || echo '{"mullvad_exit_ip":false}')

if echo "$VPN_STATUS" | grep -q '"mullvad_exit_ip":true'; then
    echo "✓ VPN: Connected to Mullvad"
    IP=$(echo "$VPN_STATUS" | grep -o '"ip":"[^"]*"' | cut -d'"' -f4)
    echo "  IP: $IP"
else
    echo "✗ VPN: NOT CONNECTED TO MULLVAD!"
    notify-send -u critical "VPN Warning" "Not connected to Mullvad VPN!"
    exit 1
fi
EOF

chmod +x ~/trading/check_vpn.sh

cat > ~/trading/start_trading.sh << 'EOF'
#!/bin/bash
# Start trading session

cd ~/trading/EleanorPlatform
source venv/bin/activate

# Check VPN first
~/trading/check_vpn.sh || exit 1

# Start trading in tmux session
tmux new-session -d -s trading "cd ~/trading/EleanorPlatform/src/eleanor && python run_paper_trading.py --capital 15000 --duration 24"

echo "✓ Trading session started in tmux"
echo "  Attach with: tmux attach -t trading"
echo "  Detach with: Ctrl+B, D"
EOF

chmod +x ~/trading/start_trading.sh

cat > ~/trading/stop_trading.sh << 'EOF'
#!/bin/bash
# Emergency stop script

echo "Stopping all trading activities..."
pkill -f "python.*paper_trading"
pkill -f "python.*run_paper_trading"
tmux kill-session -t trading 2>/dev/null || true

# Stop Docker if running
if command -v docker &> /dev/null; then
    cd ~/trading/EleanorPlatform
    docker-compose -f compose/docker-compose.yaml down 2>/dev/null || true
fi

echo "✓ Trading stopped"
EOF

chmod +x ~/trading/stop_trading.sh

# Run initial backtest
echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Quick Start:"
echo "  1. Run backtest:  cd ~/trading/EleanorPlatform && source venv/bin/activate && python run_backtest.py"
echo "  2. Start trading: ~/trading/start_trading.sh"
echo "  3. Stop trading:  ~/trading/stop_trading.sh"
echo "  4. Check VPN:     ~/trading/check_vpn.sh"
echo ""
echo "Useful commands:"
echo "  - View trading:   tmux attach -t trading"
echo "  - Monitor system: htop"
echo "  - Check network:  nethogs"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "  - Always verify VPN connection before trading"
echo "  - Start with paper trading first"
echo "  - Monitor for at least 1-2 weeks before going live"
echo ""

# Offer to run backtest
read -p "Run initial backtest now? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    echo "Running backtest (this may take a few minutes)..."
    cd ~/trading/EleanorPlatform
    source venv/bin/activate
    python run_backtest.py
fi

echo ""
echo -e "${GREEN}All done! Happy trading!${NC}"
