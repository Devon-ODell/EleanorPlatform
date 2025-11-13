#!/bin/bash
# Eleanor Platform - Comprehensive Monitoring Script for Qubes OS
# Monitors: VPN connection, system resources, trading performance, and alerts

set -euo pipefail

# Configuration
TRADING_DIR="$HOME/trading/EleanorPlatform"
RESULTS_DIR="$TRADING_DIR/src/eleanor/results"
DATA_DIR="$TRADING_DIR/src/eleanor/data"
LOG_FILE="$TRADING_DIR/logs/monitor.log"
ALERT_THRESHOLD_CAPITAL=10000  # Alert if capital drops below this
CHECK_INTERVAL=300  # 5 minutes

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Check VPN connection
check_vpn() {
    echo -e "\n${BLUE}=== VPN Status ===${NC}"

    VPN_RESPONSE=$(curl -sf --max-time 10 https://am.i.mullvad.net/json 2>/dev/null || echo '{"mullvad_exit_ip":false}')

    if echo "$VPN_RESPONSE" | jq -e '.mullvad_exit_ip == true' >/dev/null 2>&1; then
        IP=$(echo "$VPN_RESPONSE" | jq -r '.ip')
        LOCATION=$(echo "$VPN_RESPONSE" | jq -r '.country + ", " + .city' 2>/dev/null || echo "Unknown")
        echo -e "${GREEN}✓ VPN Connected${NC}"
        echo "  IP: $IP"
        echo "  Location: $LOCATION"
        log "VPN OK: $IP ($LOCATION)"
        return 0
    else
        echo -e "${RED}✗ VPN DISCONNECTED!${NC}"
        log "ERROR: VPN disconnected!"

        # Send desktop notification
        if command -v notify-send &> /dev/null; then
            notify-send -u critical "Eleanor Trading Alert" "VPN DISCONNECTED!"
        fi

        # Emergency stop if VPN is down
        if pgrep -f "python.*paper_trading" > /dev/null; then
            echo -e "${RED}Stopping trading due to VPN failure...${NC}"
            pkill -f "python.*paper_trading"
            log "EMERGENCY: Stopped trading due to VPN failure"
        fi

        return 1
    fi
}

# Check system resources
check_system() {
    echo -e "\n${BLUE}=== System Resources ===${NC}"

    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    echo "CPU Usage: ${CPU_USAGE}%"

    # Memory usage
    MEM_INFO=$(free -m | awk 'NR==2{printf "Memory: %s/%sMB (%.2f%%)", $3,$2,$3*100/$2 }')
    echo "$MEM_INFO"

    # Disk usage
    DISK_USAGE=$(df -h "$TRADING_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "Disk Usage: ${DISK_USAGE}%"

    # Check for high resource usage
    if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
        log "WARNING: High CPU usage: ${CPU_USAGE}%"
    fi

    if (( DISK_USAGE > 90 )); then
        log "WARNING: High disk usage: ${DISK_USAGE}%"
        echo -e "${YELLOW}⚠ Disk usage critical!${NC}"
    fi
}

# Check trading status
check_trading() {
    echo -e "\n${BLUE}=== Trading Status ===${NC}"

    if pgrep -f "python.*paper_trading" > /dev/null; then
        PID=$(pgrep -f "python.*paper_trading")
        UPTIME=$(ps -p "$PID" -o etime= | tr -d ' ')
        echo -e "${GREEN}✓ Trading Active${NC}"
        echo "  PID: $PID"
        echo "  Uptime: $UPTIME"
        log "Trading active: PID $PID, uptime $UPTIME"
    else
        echo -e "${YELLOW}⚠ Trading Not Running${NC}"
        log "WARNING: Trading not running"
        return 1
    fi
}

# Check trading performance
check_performance() {
    echo -e "\n${BLUE}=== Trading Performance ===${NC}"

    # Find most recent trade history file
    LATEST_TRADES=$(find "$RESULTS_DIR" -name "trade_history_*.csv" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)

    if [ -z "$LATEST_TRADES" ] || [ ! -f "$LATEST_TRADES" ]; then
        echo "No trade history found"
        return 0
    fi

    # Parse latest trades
    TOTAL_TRADES=$(tail -n +2 "$LATEST_TRADES" | wc -l)

    if [ "$TOTAL_TRADES" -eq 0 ]; then
        echo "No trades executed yet"
        return 0
    fi

    # Get latest capital value
    LATEST_CAPITAL=$(tail -1 "$LATEST_TRADES" | cut -d',' -f10)
    INITIAL_CAPITAL=15000  # From backtest config

    if [ -n "$LATEST_CAPITAL" ]; then
        PROFIT=$(echo "$LATEST_CAPITAL - $INITIAL_CAPITAL" | bc)
        RETURN_PCT=$(echo "scale=2; ($PROFIT / $INITIAL_CAPITAL) * 100" | bc)

        echo "Total Trades: $TOTAL_TRADES"
        echo "Current Capital: \$$(printf '%.2f' "$LATEST_CAPITAL")"
        echo "Profit/Loss: \$$(printf '%.2f' "$PROFIT") (${RETURN_PCT}%)"

        log "Performance: $TOTAL_TRADES trades, capital: \$$LATEST_CAPITAL, P&L: \$$PROFIT"

        # Alert if capital drops below threshold
        if (( $(echo "$LATEST_CAPITAL < $ALERT_THRESHOLD_CAPITAL" | bc -l) )); then
            echo -e "${RED}⚠ Capital below threshold!${NC}"
            log "ALERT: Capital below threshold: \$$LATEST_CAPITAL"

            if command -v notify-send &> /dev/null; then
                notify-send -u critical "Eleanor Trading Alert" "Capital dropped to \$$LATEST_CAPITAL"
            fi
        fi

        # Calculate recent performance (last 10 trades)
        RECENT_PROFIT=$(tail -10 "$LATEST_TRADES" | awk -F',' '{sum+=$7} END {print sum}')
        echo "Recent 10 trades P&L: \$$(printf '%.2f' "$RECENT_PROFIT")"
    fi
}

# Check for errors in logs
check_errors() {
    echo -e "\n${BLUE}=== Recent Errors ===${NC}"

    LOG_FILES=("$TRADING_DIR/logs/trading.log" "$TRADING_DIR/logs/trading-error.log")

    for logfile in "${LOG_FILES[@]}"; do
        if [ -f "$logfile" ]; then
            # Check for errors in last 100 lines
            ERROR_COUNT=$(tail -100 "$logfile" 2>/dev/null | grep -ic "error\|exception\|failed" || true)

            if [ "$ERROR_COUNT" -gt 0 ]; then
                echo -e "${YELLOW}Found $ERROR_COUNT errors in $(basename "$logfile")${NC}"
                echo "Last 5 errors:"
                tail -100 "$logfile" | grep -i "error\|exception\|failed" | tail -5 || true
            else
                echo "No recent errors in $(basename "$logfile")"
            fi
        fi
    done
}

# Network connectivity check
check_network() {
    echo -e "\n${BLUE}=== Network Connectivity ===${NC}"

    # Check DNS
    if nslookup google.com >/dev/null 2>&1; then
        echo -e "${GREEN}✓ DNS Resolution${NC}"
    else
        echo -e "${RED}✗ DNS Resolution Failed${NC}"
        log "ERROR: DNS resolution failed"
    fi

    # Check external connectivity
    if curl -sf --max-time 5 https://api.github.com >/dev/null 2>&1; then
        echo -e "${GREEN}✓ External Connectivity${NC}"
    else
        echo -e "${RED}✗ External Connectivity Failed${NC}"
        log "ERROR: External connectivity failed"
    fi
}

# Docker status (if using Docker)
check_docker() {
    if ! command -v docker &> /dev/null; then
        return 0
    fi

    echo -e "\n${BLUE}=== Docker Status ===${NC}"

    cd "$TRADING_DIR/compose" || return

    if docker-compose -f docker-compose.qubes.yaml ps 2>/dev/null | grep -q "Up"; then
        echo -e "${GREEN}✓ Docker containers running${NC}"
        docker-compose -f docker-compose.qubes.yaml ps --format "table {{.Service}}\t{{.Status}}"
    else
        echo "Docker containers not running"
    fi
}

# Generate summary report
generate_summary() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}    Eleanor Trading Monitor Summary    ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
}

# Main monitoring loop
main() {
    if [ "${1:-}" = "--daemon" ]; then
        log "Starting monitoring daemon..."

        while true; do
            {
                generate_summary
                check_vpn || { sleep 60; continue; }  # Skip other checks if VPN is down
                check_system
                check_trading
                check_performance
                check_network
                check_errors
                check_docker
            } | tee -a "$LOG_FILE"

            sleep "$CHECK_INTERVAL"
        done
    else
        # Single run
        generate_summary
        check_vpn
        check_system
        check_trading
        check_performance
        check_network
        check_errors
        check_docker
    fi
}

# Handle script arguments
case "${1:-}" in
    --daemon|-d)
        main --daemon
        ;;
    --vpn)
        check_vpn
        ;;
    --trading)
        check_trading
        ;;
    --performance)
        check_performance
        ;;
    --help|-h)
        echo "Eleanor Platform Monitoring Script"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (none)          Run all checks once"
        echo "  --daemon, -d    Run continuously as daemon"
        echo "  --vpn          Check VPN status only"
        echo "  --trading      Check trading status only"
        echo "  --performance  Check performance metrics only"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                # Run all checks once"
        echo "  $0 --daemon       # Run as daemon"
        echo "  $0 --vpn          # Quick VPN check"
        ;;
    *)
        main
        ;;
esac
