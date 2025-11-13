# Eleanor Platform - Scripts Directory

## Setup Scripts

### `qubes_setup.sh`
Automated setup script for deploying Eleanor Platform in a Qubes OS trading qube.

**Usage:**
```bash
chmod +x qubes_setup.sh
./qubes_setup.sh
```

**What it does:**
- Verifies Mullvad VPN connection
- Installs all dependencies (Python 3.11, packages)
- Clones Eleanor Platform repository
- Sets up Python virtual environment
- Creates monitoring and control scripts
- Optionally runs initial backtest

## Monitoring Scripts

### `monitor.sh`
Comprehensive monitoring script that checks VPN status, system resources, trading performance, and errors.

**Usage:**
```bash
# Single check
./monitor.sh

# Run as daemon (continuous monitoring)
./monitor.sh --daemon

# Check specific aspects
./monitor.sh --vpn          # VPN only
./monitor.sh --trading      # Trading status only
./monitor.sh --performance  # Performance metrics only
```

**Features:**
- VPN connection verification (Mullvad)
- System resource monitoring (CPU, RAM, disk)
- Trading bot status
- Performance metrics from trade history
- Error log analysis
- Docker container status
- Desktop notifications for alerts
- Emergency stop on VPN failure

## Service Files

### `eleanor-trading.service`
Systemd service file for running Eleanor trading bot as a system service.

**Installation:**
```bash
# Copy service file
sudo cp eleanor-trading.service /etc/systemd/system/eleanor-trading@.service

# Enable and start for your user
sudo systemctl enable eleanor-trading@$USER
sudo systemctl start eleanor-trading@$USER

# Check status
sudo systemctl status eleanor-trading@$USER

# View logs
journalctl -u eleanor-trading@$USER -f
```

**Features:**
- VPN check before starting
- Automatic restart on failure
- Security hardening (limited privileges)
- Resource limits
- Logging to files

## Quick Start Scripts

Created by `qubes_setup.sh` in `~/trading/`:

### `start_trading.sh`
Starts trading session in tmux with VPN verification.

### `stop_trading.sh`
Emergency stop script - kills all trading processes.

### `check_vpn.sh`
Quick VPN status check with desktop notification on failure.

## Example Workflows

### Initial Setup
```bash
# 1. Run setup in trading qube
./qubes_setup.sh

# 2. Start monitoring daemon
./monitor.sh --daemon &

# 3. Start trading
~/trading/start_trading.sh
```

### Regular Monitoring
```bash
# Check everything
./monitor.sh

# Monitor continuously
tmux new -s monitor
./monitor.sh --daemon
# Detach: Ctrl+B, D
```

### Emergency Stop
```bash
~/trading/stop_trading.sh
```

### Service-based Deployment
```bash
# Install service
sudo cp scripts/eleanor-trading.service /etc/systemd/system/eleanor-trading@.service
sudo systemctl enable eleanor-trading@$USER
sudo systemctl start eleanor-trading@$USER

# Monitor
sudo systemctl status eleanor-trading@$USER
journalctl -u eleanor-trading@$USER -f
```

## Cron Jobs

Add to crontab for automated monitoring:

```bash
crontab -e
```

Add:
```cron
# Monitor every 15 minutes
*/15 * * * * /home/user/trading/check_vpn.sh

# Full monitor check every hour
0 * * * * /home/user/trading/EleanorPlatform/scripts/monitor.sh

# Daily performance report
0 9 * * * /home/user/trading/EleanorPlatform/scripts/monitor.sh --performance
```

## Security Notes

All scripts include:
- VPN verification before sensitive operations
- Emergency stop on VPN failure
- Desktop notifications for critical events
- Comprehensive logging
- Minimal privileges (no unnecessary root)

## Logs

Scripts log to:
- `~/trading/EleanorPlatform/logs/monitor.log` - Monitoring events
- `~/trading/EleanorPlatform/logs/trading.log` - Trading bot output
- `~/trading/EleanorPlatform/logs/trading-error.log` - Error messages

## Troubleshooting

### Scripts won't execute
```bash
chmod +x scripts/*.sh
chmod +x ~/trading/*.sh
```

### VPN checks failing
```bash
# Verify Mullvad connection manually
curl https://am.i.mullvad.net/json

# Check sys-vpn qube status (in dom0)
qvm-check sys-vpn
```

### Monitoring daemon stopped
```bash
# Check if running
pgrep -f monitor.sh

# Restart
nohup ./scripts/monitor.sh --daemon > /dev/null 2>&1 &
```

### Service won't start
```bash
# Check service status
sudo systemctl status eleanor-trading@$USER

# View recent logs
journalctl -u eleanor-trading@$USER -n 50

# Test VPN manually
curl https://am.i.mullvad.net/json
```
