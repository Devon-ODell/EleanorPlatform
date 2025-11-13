#!/bin/bash
# Dual VPN Setup for Raspberry Pi
# Creates separate network namespaces for scraping and management

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Eleanor Platform - Dual VPN Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}[1/6] Checking dependencies...${NC}"
DEPS="ip iptables jq curl"
for dep in $DEPS; do
    if ! command -v $dep &> /dev/null; then
        echo -e "${RED}❌ Missing dependency: $dep${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All dependencies found${NC}"

# Install Mullvad if not present
echo -e "${BLUE}[2/6] Checking Mullvad VPN...${NC}"
if ! command -v mullvad &> /dev/null; then
    echo -e "${YELLOW}Installing Mullvad VPN...${NC}"

    # Download Mullvad
    wget -q https://mullvad.net/download/app/deb/latest -O /tmp/mullvad.deb
    dpkg -i /tmp/mullvad.deb || apt-get install -f -y
    rm /tmp/mullvad.deb

    echo -e "${YELLOW}⚠️  Please configure Mullvad account:${NC}"
    echo -e "   Run: ${GREEN}mullvad account login YOUR_ACCOUNT_NUMBER${NC}"
    echo -e "   Then re-run this script"
    exit 1
fi

# Check Mullvad connection
if ! mullvad status | grep -q "Connected"; then
    echo -e "${YELLOW}Connecting to Mullvad...${NC}"
    mullvad connect
    sleep 5
fi

MULLVAD_STATUS=$(curl -s https://am.i.mullvad.net/json)
if echo "$MULLVAD_STATUS" | jq -e '.mullvad_exit_ip == true' > /dev/null; then
    echo -e "${GREEN}✓ Mullvad VPN connected${NC}"
    echo -e "  IP: $(echo $MULLVAD_STATUS | jq -r '.ip')"
    echo -e "  Location: $(echo $MULLVAD_STATUS | jq -r '.city'), $(echo $MULLVAD_STATUS | jq -r '.country')"
else
    echo -e "${RED}❌ Mullvad not connected properly${NC}"
    exit 1
fi

# Get Mullvad interface
MULLVAD_IF=$(ip route | grep default | grep -o 'dev [^ ]*' | awk '{print $2}' | head -1)
echo -e "${BLUE}Mullvad interface: ${MULLVAD_IF}${NC}"

# Create scraping namespace
echo -e "${BLUE}[3/6] Creating network namespace for scraping...${NC}"

# Delete old namespace if exists
ip netns del vpn-scraping 2>/dev/null || true
ip link del veth-scrape-a 2>/dev/null || true

# Create namespace
ip netns add vpn-scraping
echo -e "${GREEN}✓ Created vpn-scraping namespace${NC}"

# Create veth pair
ip link add veth-scrape-a type veth peer name veth-scrape-b
ip link set veth-scrape-b netns vpn-scraping

# Configure host side
ip addr add 10.200.1.1/24 dev veth-scrape-a
ip link set veth-scrape-a up

# Configure namespace side
ip netns exec vpn-scraping ip addr add 10.200.1.2/24 dev veth-scrape-b
ip netns exec vpn-scraping ip link set veth-scrape-b up
ip netns exec vpn-scraping ip link set lo up
ip netns exec vpn-scraping ip route add default via 10.200.1.1

echo -e "${GREEN}✓ Configured veth pair${NC}"

# Enable IP forwarding
echo -e "${BLUE}[4/6] Enabling IP forwarding...${NC}"
sysctl -w net.ipv4.ip_forward=1 > /dev/null
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-eleanor-vpn.conf
echo -e "${GREEN}✓ IP forwarding enabled${NC}"

# Configure NAT
echo -e "${BLUE}[5/6] Configuring NAT and firewall rules...${NC}"

# Clear old rules
iptables -t nat -D POSTROUTING -s 10.200.1.0/24 -o $MULLVAD_IF -j MASQUERADE 2>/dev/null || true
iptables -D FORWARD -i veth-scrape-a -o $MULLVAD_IF -j ACCEPT 2>/dev/null || true
iptables -D FORWARD -i $MULLVAD_IF -o veth-scrape-a -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true

# Add NAT rule
iptables -t nat -A POSTROUTING -s 10.200.1.0/24 -o $MULLVAD_IF -j MASQUERADE
iptables -A FORWARD -i veth-scrape-a -o $MULLVAD_IF -j ACCEPT
iptables -A FORWARD -i $MULLVAD_IF -o veth-scrape-a -m state --state RELATED,ESTABLISHED -j ACCEPT

# Save iptables rules
iptables-save > /etc/iptables/rules.v4 2>/dev/null || true

echo -e "${GREEN}✓ NAT configured${NC}"

# Configure DNS for namespace
echo -e "${BLUE}[6/6] Configuring DNS...${NC}"
mkdir -p /etc/netns/vpn-scraping
cat > /etc/netns/vpn-scraping/resolv.conf <<EOF
# Mullvad DNS (ad-blocking)
nameserver 10.64.0.1
# Cloudflare DNS (backup)
nameserver 1.1.1.1
nameserver 1.0.0.1
EOF
echo -e "${GREEN}✓ DNS configured${NC}"

# Test namespace connectivity
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Testing VPN Namespace${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo -e "${BLUE}Host VPN Status:${NC}"
curl -s https://am.i.mullvad.net/json | jq '{ip, city, country, mullvad_exit_ip}'

echo
echo -e "${BLUE}Namespace VPN Status:${NC}"
ip netns exec vpn-scraping curl -s https://am.i.mullvad.net/json | jq '{ip, city, country, mullvad_exit_ip}'

echo
if ip netns exec vpn-scraping curl -s https://am.i.mullvad.net/json | jq -e '.mullvad_exit_ip == true' > /dev/null; then
    echo -e "${GREEN}✅ SUCCESS: Scraping namespace is using Mullvad VPN${NC}"
else
    echo -e "${RED}❌ FAILED: Namespace not using VPN${NC}"
    exit 1
fi

# Create systemd service for persistence
echo
echo -e "${BLUE}Creating systemd service for persistence...${NC}"

cat > /etc/systemd/system/eleanor-vpn-namespace.service <<EOF
[Unit]
Description=Eleanor Platform VPN Network Namespace
After=network-online.target mullvad-daemon.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/setup-eleanor-vpn-namespace.sh
RemainAfterExit=yes
StandardOutput=journal

[Install]
WantedBy=multi-user.target
EOF

# Copy this script to /usr/local/bin
cp "$0" /usr/local/bin/setup-eleanor-vpn-namespace.sh
chmod +x /usr/local/bin/setup-eleanor-vpn-namespace.sh

# Enable service
systemctl daemon-reload
systemctl enable eleanor-vpn-namespace.service

echo -e "${GREEN}✓ Systemd service created and enabled${NC}"

echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Dual VPN Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${GREEN}Usage:${NC}"
echo -e "  Run command in scraping namespace:"
echo -e "  ${BLUE}sudo ip netns exec vpn-scraping <command>${NC}"
echo
echo -e "  Example:"
echo -e "  ${BLUE}sudo ip netns exec vpn-scraping curl https://am.i.mullvad.net/json${NC}"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Install Tailscale for secure management access"
echo -e "  2. Start Eleanor Platform with:"
echo -e "     ${BLUE}docker-compose -f docker-compose.pi.yml up -d${NC}"
echo
