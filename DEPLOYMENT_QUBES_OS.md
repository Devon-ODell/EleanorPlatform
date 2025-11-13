# Deploying Eleanor DeFi Arbitrage on Qubes OS with Mullvad VPN

## Overview

This guide covers deploying the Eleanor Platform DeFi arbitrage system on Qubes OS with Mullvad VPN protection for enhanced privacy and security.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Qubes OS                          │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         sys-vpn (Mullvad VPN)                │  │
│  │  - VPN connection to Mullvad                 │  │
│  │  - Network gateway for trading qube          │  │
│  └────────────────┬─────────────────────────────┘  │
│                   │                                  │
│  ┌────────────────▼─────────────────────────────┐  │
│  │         trading-qube (AppVM)                 │  │
│  │  - Eleanor Platform                          │  │
│  │  - Python 3.11+                              │  │
│  │  - Docker (optional, for Hummingbot)         │  │
│  │  - All traffic routed through sys-vpn        │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         vault (AppVM - offline)              │  │
│  │  - Private keys storage                      │  │
│  │  - Wallet seeds (encrypted)                  │  │
│  │  - API credentials                           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

- Qubes OS 4.1+ installed
- Mullvad VPN account and configuration
- 8GB+ RAM (recommended 16GB for multiple VMs)
- 50GB+ free disk space

## Step 1: Set Up Mullvad VPN Qube

### 1.1 Create VPN Template (if not exists)

```bash
# In dom0
qvm-clone fedora-38 fedora-38-vpn
qvm-run -u root fedora-38-vpn gnome-terminal
```

In the VPN template terminal:
```bash
# Install Mullvad VPN client
sudo dnf install -y wireguard-tools openvpn
curl -fsSLO https://mullvad.net/media/app/MullvadVPN-2024.5_amd64.rpm
sudo dnf install -y ./MullvadVPN-2024.5_amd64.rpm

# Or use WireGuard configuration
sudo dnf install -y wireguard-tools
```

### 1.2 Create sys-vpn Qube

```bash
# In dom0
qvm-create -t fedora-38-vpn -l red sys-vpn --property netvm=sys-firewall
qvm-prefs sys-vpn provides_network true
qvm-prefs sys-vpn autostart true
qvm-start sys-vpn
```

### 1.3 Configure Mullvad in sys-vpn

Option A: Using Mullvad App
```bash
# In sys-vpn
mullvad account login <your-account-number>
mullvad auto-connect set on
mullvad lan set allow
mullvad connect
```

Option B: Using WireGuard Config
```bash
# Download config from Mullvad website
# Copy to sys-vpn: /rw/config/mullvad.conf

sudo mkdir -p /rw/config/wireguard
sudo cp /path/to/mullvad.conf /rw/config/wireguard/wg0.conf
sudo chmod 600 /rw/config/wireguard/wg0.conf

# Create startup script
sudo nano /rw/config/rc.local
```

Add to rc.local:
```bash
#!/bin/bash
wg-quick up /rw/config/wireguard/wg0.conf
```

```bash
sudo chmod +x /rw/config/rc.local
```

### 1.4 Test VPN Connection

```bash
# In sys-vpn
curl https://am.i.mullvad.net/json
# Should show: "mullvad_exit_ip": true
```

### 1.5 Configure DNS Leak Protection

```bash
# In sys-vpn
sudo nano /rw/config/qubes-firewall-user-script
```

Add:
```bash
#!/bin/bash
# Block all DNS except through VPN
iptables -I OUTPUT -p udp --dport 53 -j REJECT
iptables -I OUTPUT -p tcp --dport 53 -j REJECT
ip6tables -I OUTPUT -p udp --dport 53 -j REJECT
ip6tables -I OUTPUT -p tcp --dport 53 -j REJECT

# Allow DNS through VPN interface
iptables -I OUTPUT -o wg0 -p udp --dport 53 -j ACCEPT
iptables -I OUTPUT -o wg0 -p tcp --dport 53 -j ACCEPT
```

```bash
sudo chmod +x /rw/config/qubes-firewall-user-script
```

## Step 2: Create Trading Qube

### 2.1 Create Trading AppVM

```bash
# In dom0
qvm-create -t debian-12 -l green trading-qube
qvm-prefs trading-qube netvm sys-vpn
qvm-prefs trading-qube vcpus 4
qvm-prefs trading-qube memory 4096
qvm-prefs trading-qube maxmem 8192
qvm-volume extend trading-qube:private 50GB
qvm-start trading-qube
```

### 2.2 Install Dependencies

```bash
# In trading-qube
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git \
    build-essential curl wget gnupg2 software-properties-common

# Install Python 3.11+ if needed
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

### 2.3 Clone Eleanor Platform

```bash
# In trading-qube
mkdir -p ~/trading
cd ~/trading

# Option 1: Clone from GitHub
git clone https://github.com/Devon-ODell/EleanorPlatform.git
cd EleanorPlatform
git checkout claude/hummingbot-defi-backtest-011CUvp5TPEuvpevnFLxgEAc

# Option 2: Transfer from vault using qvm-copy
# If you have the code in vault qube:
# qvm-copy /path/to/EleanorPlatform
```

### 2.4 Set Up Python Environment

```bash
cd ~/trading/EleanorPlatform
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.5 Verify VPN Connection

```bash
# Verify all traffic goes through Mullvad
curl https://am.i.mullvad.net/json
# Should show Mullvad IP and "mullvad_exit_ip": true
```

## Step 3: Security Hardening

### 3.1 Create Vault Qube for Secrets

```bash
# In dom0
qvm-create -t debian-12 -l black vault
qvm-prefs vault netvm ""  # Completely offline
qvm-start vault
```

### 3.2 Store Credentials Securely

In vault qube:
```bash
# Create encrypted credentials file
mkdir -p ~/secrets
nano ~/secrets/.env

# Add your credentials (never copy to online qubes)
# WALLET_PRIVATE_KEY=your_key_here
# API_KEY=your_api_key
# etc.

# Encrypt the file
gpg --symmetric --cipher-algo AES256 ~/secrets/.env
shred -vfz -n 10 ~/secrets/.env
```

### 3.3 Transfer Credentials Safely

When needed in trading-qube:
```bash
# In vault (only when absolutely necessary)
qvm-copy ~/secrets/.env.gpg

# In trading-qube
cd ~/QubesIncoming/vault/
gpg --decrypt .env.gpg > ~/.env
chmod 600 ~/.env
# Delete after use if running paper trading
```

### 3.4 Set Up Firewall Rules

```bash
# In dom0 - restrict trading-qube connections
qvm-firewall trading-qube reset
qvm-firewall trading-qube add accept dsthost=api.mullvad.net
qvm-firewall trading-qube add accept proto=tcp dstports=443 # HTTPS
qvm-firewall trading-qube add accept proto=tcp dstports=80  # HTTP
qvm-firewall trading-qube add drop
```

For production (allow specific DEX/RPC endpoints):
```bash
# Allow Infura/Alchemy/Ankr RPC endpoints
qvm-firewall trading-qube add accept dsthost=mainnet.infura.io
qvm-firewall trading-qube add accept dsthost=eth-mainnet.g.alchemy.com
qvm-firewall trading-qube add accept dsthost=rpc.ankr.com

# Allow DEX subgraph APIs
qvm-firewall trading-qube add accept dsthost=api.thegraph.com
```

## Step 4: Run Paper Trading

### 4.1 Test Backtest First

```bash
# In trading-qube
cd ~/trading/EleanorPlatform
source venv/bin/activate
python run_backtest.py
```

### 4.2 Start Paper Trading Session

```bash
# 24-hour paper trading session
cd src/eleanor
python run_paper_trading.py --capital 15000 --duration 24

# Or shorter test
python run_paper_trading.py --capital 1000 --duration 1 --interval 60
```

### 4.3 Monitor with Screen/Tmux

```bash
sudo apt install -y tmux
tmux new -s trading
cd ~/trading/EleanorPlatform/src/eleanor
python run_paper_trading.py --capital 15000 --duration 24

# Detach: Ctrl+B, D
# Reattach: tmux attach -t trading
```

## Step 5: Docker Deployment (Optional - for Hummingbot)

### 5.1 Install Docker in Trading Qube

```bash
# In trading-qube
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### 5.2 Deploy with Docker Compose

```bash
cd ~/trading/EleanorPlatform
docker-compose -f compose/docker-compose.yaml up -d

# Check logs
docker-compose -f compose/docker-compose.yaml logs -f
```

### 5.3 Access n8n Workflow UI

```bash
# In dom0, open browser in trading-qube
qvm-run trading-qube firefox http://localhost:2222
# Login with credentials from compose/.env
```

## Step 6: Production Deployment

### 6.1 Enable Persistence

```bash
# In trading-qube, create bind-dirs for persistence
sudo mkdir -p /rw/bind-dirs/opt/eleanor
sudo nano /rw/config/qubes-bind-dirs.d/50_user.conf
```

Add:
```
binds+=( '/opt/eleanor' )
```

### 6.2 Create Systemd Service

```bash
sudo nano /etc/systemd/system/eleanor-trading.service
```

Add:
```ini
[Unit]
Description=Eleanor DeFi Arbitrage Trading
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/trading/EleanorPlatform/src/eleanor
Environment="PATH=/home/user/trading/EleanorPlatform/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/user/trading/EleanorPlatform/venv/bin/python run_paper_trading.py --capital 15000 --duration 168
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable eleanor-trading
sudo systemctl start eleanor-trading
sudo systemctl status eleanor-trading
```

### 6.3 Set Up Auto-start

```bash
# In dom0
qvm-prefs trading-qube autostart true
```

## Step 7: Monitoring and Logging

### 7.1 Set Up Log Rotation

```bash
# In trading-qube
sudo nano /etc/logrotate.d/eleanor
```

Add:
```
/home/user/trading/EleanorPlatform/src/eleanor/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 7.2 Monitor System Resources

```bash
# Install monitoring tools
sudo apt install -y htop nethogs iotop

# Monitor in real-time
htop
# Network: nethogs
# Disk I/O: sudo iotop
```

### 7.3 Set Up Alerts

Create monitoring script:
```bash
nano ~/trading/monitor.sh
```

```bash
#!/bin/bash
# Monitor capital and send alerts

CAPITAL=$(tail -1 ~/trading/EleanorPlatform/src/eleanor/data/capital.log | awk '{print $2}')
THRESHOLD=10000

if [ $(echo "$CAPITAL < $THRESHOLD" | bc) -eq 1 ]; then
    notify-send "Eleanor Trading Alert" "Capital below threshold: $CAPITAL"
fi
```

```bash
chmod +x ~/trading/monitor.sh
# Add to crontab: */15 * * * * ~/trading/monitor.sh
```

## Security Best Practices

### 1. **Never Mix Wallets**
- Use separate wallets for DeFi arbitrage vs. long-term holdings
- Keep seed phrases in vault qube only

### 2. **Minimize Attack Surface**
- Keep trading-qube minimal (no browser, no email)
- Only install necessary packages
- Regularly update all software

### 3. **Monitor for Anomalies**
- Check VPN connection hourly: `curl https://am.i.mullvad.net/json`
- Monitor gas prices for unusual spikes
- Watch for failed transactions (possible front-running)

### 4. **Backup Strategy**
```bash
# In dom0 - backup trading qube regularly
qvm-backup trading-qube /path/to/backup/

# Backup results from trading-qube
qvm-run trading-qube "tar czf ~/trading-backup.tar.gz ~/trading/EleanorPlatform/src/eleanor/results"
qvm-copy-to-dom0 ~/trading-backup.tar.gz ~/backups/
```

### 5. **Kill Switch**
Create emergency stop script in trading-qube:
```bash
nano ~/kill_trading.sh
```

```bash
#!/bin/bash
sudo systemctl stop eleanor-trading
docker-compose -f ~/trading/EleanorPlatform/compose/docker-compose.yaml down
pkill -f "python.*paper_trading"
```

```bash
chmod +x ~/kill_trading.sh
```

## Troubleshooting

### VPN Connection Lost

```bash
# In sys-vpn
sudo wg-quick down wg0
sudo wg-quick up /rw/config/wireguard/wg0.conf

# Or restart Mullvad
mullvad reconnect
```

### Trading Qube Can't Connect

```bash
# Check VPN status
curl https://am.i.mullvad.net/json

# Check DNS
nslookup google.com

# Check firewall rules (in dom0)
qvm-firewall trading-qube list
```

### High Memory Usage

```bash
# In dom0, increase memory allocation
qvm-prefs trading-qube memory 8192
qvm-prefs trading-qube maxmem 12288
```

### Docker Issues

```bash
# Restart Docker
sudo systemctl restart docker

# Check Docker logs
docker-compose -f compose/docker-compose.yaml logs
```

## Performance Optimization

### 1. **Use Dedicated CPU Cores**
```bash
# In dom0
qvm-prefs trading-qube vcpus 4
```

### 2. **Increase I/O Priority**
```bash
# In trading-qube
sudo ionice -c1 -n0 -p $(pgrep -f python.*paper_trading)
```

### 3. **Use RAM Disk for Temporary Data**
```bash
sudo mkdir /mnt/ramdisk
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk
```

## Cost Estimates

**Mullvad VPN:** €5/month
**Qubes OS:** Free (open source)
**VPS Alternative:** Not needed (runs on your hardware)

**Hardware Requirements:**
- CPU: 4+ cores (6+ recommended)
- RAM: 16GB minimum (32GB recommended for smooth operation)
- Disk: 100GB+ SSD

## Next Steps

1. ✅ Set up Qubes OS with Mullvad VPN
2. ✅ Create trading qube and vault qube
3. ✅ Deploy Eleanor Platform
4. ✅ Run backtests to verify setup
5. ✅ Start paper trading with small capital
6. ⏸️ Monitor for 1-2 weeks
7. ⏸️ Gradually increase capital if profitable
8. ⏸️ Consider live trading with Hummingbot

## Additional Resources

- [Qubes OS Documentation](https://www.qubes-os.org/doc/)
- [Mullvad VPN Setup Guide](https://mullvad.net/en/help/wireguard-and-mullvad-vpn/)
- [Hummingbot Documentation](https://docs.hummingbot.org/)
- [DeFi Security Best Practices](https://blog.chain.link/defi-security-best-practices/)

---

**⚠️ IMPORTANT DISCLAIMER:**

This setup provides strong privacy and security, but **DeFi trading still involves significant financial risk**. Always:
- Start with small amounts
- Never invest more than you can afford to lose
- Understand the tax implications in your jurisdiction
- Ensure compliance with local laws regarding cryptocurrency trading

**Your privacy setup (Mullvad + Qubes) does not protect against:**
- Smart contract bugs
- Market manipulation
- Front-running by MEV bots
- Exchange/DEX failures
- Blockchain analysis (all transactions are public)
