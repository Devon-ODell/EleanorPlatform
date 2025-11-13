#!/bin/bash
# Complete Raspberry Pi Setup for Eleanor Platform
# One-command deployment with dual VPN + post-quantum SSH

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Eleanor Platform - Complete Raspberry Pi Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${YELLOW}This script will configure:${NC}"
echo -e "  ✅ System updates and dependencies"
echo -e "  ✅ Docker and Docker Compose"
echo -e "  ✅ Post-quantum SSH encryption"
echo -e "  ✅ Dual VPN setup (Mullvad + Tailscale)"
echo -e "  ✅ Eleanor Platform arbitrage bot"
echo -e "  ✅ Monitoring stack (Prometheus + Grafana)"
echo
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Get actual user
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo
echo -e "${BLUE}[1/10] Updating system...${NC}"
apt-get update -qq
apt-get upgrade -y -qq
echo -e "${GREEN}✓ System updated${NC}"

echo
echo -e "${BLUE}[2/10] Installing essential packages...${NC}"
apt-get install -y -qq \
    git curl wget vim htop \
    build-essential \
    python3 python3-pip python3-venv \
    docker.io docker-compose \
    wireguard wireguard-tools \
    iptables iproute2 iptables-persistent \
    ufw fail2ban \
    jq netcat \
    chromium chromium-driver

echo -e "${GREEN}✓ Essential packages installed${NC}"

echo
echo -e "${BLUE}[3/10] Configuring Docker...${NC}"
usermod -aG docker $ACTUAL_USER
systemctl enable docker
systemctl start docker
echo -e "${GREEN}✓ Docker configured${NC}"

echo
echo -e "${BLUE}[4/10] Optimizing Raspberry Pi performance...${NC}"

# GPU memory
if ! grep -q "gpu_mem=256" /boot/firmware/config.txt 2>/dev/null; then
    echo "gpu_mem=256" >> /boot/firmware/config.txt
fi

# Swap
if [ -f /etc/dphys-swapfile ]; then
    dphys-swapfile swapoff
    sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
    dphys-swapfile setup
    dphys-swapfile swapon
fi

# Sysctl optimizations
cat > /etc/sysctl.d/99-eleanor.conf <<EOF
# Network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# IP forwarding for VPN
net.ipv4.ip_forward = 1

# Connection tracking
net.netfilter.nf_conntrack_max = 262144
EOF

sysctl -p /etc/sysctl.d/99-eleanor.conf > /dev/null

echo -e "${GREEN}✓ Performance optimized${NC}"

echo
echo -e "${BLUE}[5/10] Configuring firewall...${NC}"

# Reset UFW
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH from local network
ufw allow in on eth0 from 192.168.0.0/16 to any port 22 comment 'SSH from local network'

# Enable UFW
ufw --force enable

echo -e "${GREEN}✓ Firewall configured${NC}"

echo
echo -e "${BLUE}[6/10] Configuring Fail2Ban...${NC}"

cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = root@localhost
sendername = Fail2Ban

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

echo -e "${GREEN}✓ Fail2Ban configured${NC}"

echo
echo -e "${BLUE}[7/10] Installing Tailscale (secure remote access)...${NC}"

if ! command -v tailscale &> /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
    echo -e "${GREEN}✓ Tailscale installed${NC}"

    echo -e "${YELLOW}⚠️  Please configure Tailscale:${NC}"
    echo -e "   Run: ${GREEN}sudo tailscale up${NC}"
    echo -e "   Then access via Tailscale IP from anywhere!"
else
    echo -e "${GREEN}✓ Tailscale already installed${NC}"
fi

# Allow SSH from Tailscale
if [ -f /sys/class/net/tailscale0/operstate ]; then
    ufw allow in on tailscale0 to any port 22 comment 'SSH via Tailscale'
    ufw allow in on tailscale0 to any port 3000 comment 'Grafana via Tailscale'
fi

echo
echo -e "${BLUE}[8/10] Configuring Eleanor Platform...${NC}"

# Clone repository if not already in it
if [ ! -d "$USER_HOME/EleanorPlatform" ]; then
    cd "$USER_HOME"
    sudo -u $ACTUAL_USER git clone https://github.com/Devon-ODell/EleanorPlatform.git
    cd EleanorPlatform
else
    cd "$USER_HOME/EleanorPlatform"
    sudo -u $ACTUAL_USER git pull
fi

# Create .env if doesn't exist
if [ ! -f .env ]; then
    sudo -u $ACTUAL_USER cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file - please configure passwords!${NC}"
fi

# Create necessary directories
mkdir -p data/arbitrage logs monitoring/prometheus/data monitoring/grafana/data
chown -R $ACTUAL_USER:$ACTUAL_USER .

echo -e "${GREEN}✓ Eleanor Platform configured${NC}"

echo
echo -e "${BLUE}[9/10] Installing Mullvad VPN...${NC}"

if ! command -v mullvad &> /dev/null; then
    echo -e "${YELLOW}Downloading Mullvad...${NC}"
    wget -q https://mullvad.net/download/app/deb/latest -O /tmp/mullvad.deb
    dpkg -i /tmp/mullvad.deb || apt-get install -f -y
    rm /tmp/mullvad.deb
    echo -e "${GREEN}✓ Mullvad installed${NC}"

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  IMPORTANT: Mullvad Configuration Required${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "1. Get a Mullvad account:"
    echo -e "   ${BLUE}https://mullvad.net/en/pricing${NC}"
    echo
    echo -e "2. Login:"
    echo -e "   ${GREEN}mullvad account login YOUR_ACCOUNT_NUMBER${NC}"
    echo
    echo -e "3. Connect:"
    echo -e "   ${GREEN}mullvad connect${NC}"
    echo
    echo -e "4. Re-run this script to continue setup"
    echo
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Mullvad already installed${NC}"

    # Check if connected
    if ! mullvad status | grep -q "Connected"; then
        echo -e "${YELLOW}Mullvad not connected. Please connect:${NC}"
        echo -e "  ${GREEN}mullvad connect${NC}"
        exit 0
    fi
fi

echo
echo -e "${BLUE}[10/10] Final setup steps...${NC}"

# Make scripts executable
chmod +x setup-dual-vpn.sh configure-pq-ssh.sh start_monitoring.sh

echo -e "${GREEN}✓ Setup scripts prepared${NC}"

# Print next steps
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Basic Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo
echo -e "1. ${BLUE}Configure Post-Quantum SSH:${NC}"
echo -e "   ${GREEN}sudo ./configure-pq-ssh.sh${NC}"
echo
echo -e "2. ${BLUE}Setup Dual VPN Network:${NC}"
echo -e "   ${GREEN}sudo ./setup-dual-vpn.sh${NC}"
echo
echo -e "3. ${BLUE}Configure environment:${NC}"
echo -e "   ${GREEN}nano .env${NC}  # Change passwords!"
echo
echo -e "4. ${BLUE}Start Eleanor Platform:${NC}"
echo -e "   ${GREEN}docker-compose -f docker-compose.pi.yml up -d${NC}"
echo
echo -e "5. ${BLUE}Access Grafana (via Tailscale):${NC}"
echo -e "   ${GREEN}ssh -L 3000:localhost:3000 $ACTUAL_USER@raspberrypi${NC}"
echo -e "   Open: ${BLUE}http://localhost:3000${NC}"
echo
echo -e "${YELLOW}Reboot recommended before continuing:${NC}"
echo -e "   ${GREEN}sudo reboot${NC}"
echo
