# Eleanor Platform - Monitoring Setup Guide

Complete guide for setting up Prometheus + Grafana monitoring with secure dashboard publishing.

---

## 📊 Overview

This monitoring stack provides real-time visibility into your DeFi arbitrage trading bot:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Beautiful dashboards and visualization
- **Metrics Exporter**: Custom Python exporter in the orchestrator

### Key Metrics Tracked

- 💰 **Trading Performance**: Capital, profit/loss, win rate, return %
- 📈 **Trade Execution**: Success/failure rates, trade sizes, profit percentages
- 🤖 **AI Performance**: Confidence scores, risk assessments, signal generation
- 🕷️ **Scraping**: Duration, DEX price points collected, pairs scraped
- ⚡ **System**: Uptime, cycle duration, error rates

---

## 🚀 Quick Start (Local)

### Prerequisites

- Docker & Docker Compose installed
- 4GB+ RAM available
- Ports 3000, 8000, 9090 available

### 1. Start the Monitoring Stack

```bash
# Clone repository
git clone https://github.com/Devon-ODell/EleanorPlatform.git
cd EleanorPlatform

# Configure environment (IMPORTANT: Change passwords!)
cp .env.example .env
nano .env  # Edit passwords and settings

# Start services
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Access Dashboards

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Grafana** | http://localhost:3000 | admin / eleanor2025 |
| **Prometheus** | http://localhost:9090 | None (no auth) |
| **Metrics** | http://localhost:8000/metrics | None (raw metrics) |

### 3. Verify Everything Works

```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Test metrics endpoint
curl http://localhost:8000/metrics
```

You should see metrics like:
```
arbitrage_capital_usd 15000.0
arbitrage_trades_total{priority="high",status="success"} 42
arbitrage_win_rate 1.0
...
```

---

## 📈 Dashboard Overview

The pre-configured Grafana dashboard includes:

### Top Row - Key Metrics
- **Current Capital** (gauge): Real-time capital in USD
- **Capital Over Time** (line graph): Historical capital tracking

### Performance Metrics
- **Successful Trades Rate**: Trades per minute
- **Win Rate**: Percentage of successful trades
- **Total Return %**: Overall return since start
- **Total Profit**: Cumulative profit in USD

### Trading Analysis
- **Trade Execution**: Success vs failed trades (5-min rate)
- **Trades by Priority**: Distribution of high/medium/low priority trades
- **Opportunities by DEX**: Which DEXs provide most opportunities

### System Performance
- **Scrape Duration**: p50 and p95 latency
- **AI Signals Generated**: Signal generation rate by priority
- **DEX Price Points**: Table showing data collection by DEX

---

## 🔒 Security Hardening

### 1. Change Default Passwords

**CRITICAL**: Never use default passwords in production!

```bash
# Edit .env file
nano .env

# Set strong passwords:
GRAFANA_ADMIN_PASSWORD=<use-strong-password>
GRAFANA_SECRET_KEY=<generate-with: openssl rand -hex 32>
```

### 2. Enable Grafana Authentication

Edit `docker-compose.monitoring.yml`:

```yaml
grafana:
  environment:
    # Disable anonymous access
    - GF_AUTH_ANONYMOUS_ENABLED=false

    # Enable authentication
    - GF_AUTH_BASIC_ENABLED=true

    # Optional: Enable 2FA (requires SMTP)
    - GF_AUTH_BASIC_ENABLED=true
```

### 3. Firewall Configuration

```bash
# Only allow localhost access to metrics
sudo ufw deny 8000/tcp
sudo ufw allow from 172.17.0.0/16 to any port 8000  # Docker network only

# Only allow localhost access to Prometheus
sudo ufw deny 9090/tcp

# Grafana (only if you want remote access)
sudo ufw allow 3000/tcp  # Remove this line for local-only
```

### 4. Reverse Proxy with Nginx (Optional)

```nginx
# /etc/nginx/sites-available/grafana
server {
    listen 443 ssl;
    server_name dashboard.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🌐 Publishing Dashboard to GitHub Pages

### Option 1: Static Landing Page (Recommended)

A static HTML page with setup instructions (already created).

```bash
# Enable GitHub Pages
# 1. Go to GitHub repository settings
# 2. Pages section → Source: main branch, /docs folder
# 3. Your dashboard info will be at: https://yourusername.github.io/EleanorPlatform/
```

**Pros:**
- ✅ Complete privacy (no live data exposed)
- ✅ Shows how to access dashboard
- ✅ No security concerns

**Cons:**
- ❌ Not showing live metrics

### Option 2: Grafana Cloud (Public Dashboard)

Host dashboard on Grafana Cloud with authentication.

```bash
# 1. Sign up for Grafana Cloud
https://grafana.com/auth/sign-up/create-user

# 2. Create a new stack

# 3. Configure Prometheus remote write
# Add to prometheus.yml:
remote_write:
  - url: https://<your-instance>.grafana.net/api/prom/push
    basic_auth:
      username: <instance-id>
      password: <api-key>

# 4. Import dashboard
# Upload monitoring/grafana/dashboards/eleanor_arbitrage.json

# 5. Share dashboard
# Dashboard Settings → General → Public → Enable public dashboard
```

**Security Settings:**
- Enable time range restriction
- Hide query inspector
- Set viewer permissions only
- Use snapshot feature for one-time shares

**Pros:**
- ✅ Live metrics visible
- ✅ Remote access
- ✅ Free tier available

**Cons:**
- ⚠️ Public metrics (consider privacy)
- ⚠️ Requires cloud service

### Option 3: Self-Hosted with Cloudflare Tunnel

Expose local Grafana securely using Cloudflare Tunnel (zero trust).

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create eleanor-dashboard

# Create config
cat > ~/.cloudflared/config.yml <<EOF
tunnel: <tunnel-id>
credentials-file: /home/user/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: dashboard.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel run eleanor-dashboard

# Or install as service
sudo cloudflared service install
sudo systemctl start cloudflared
```

**Add Cloudflare Access (Authentication):**
```bash
# In Cloudflare Dashboard:
# 1. Zero Trust → Access → Applications
# 2. Add Application → Self-hosted
# 3. Set authentication rules (email, GitHub, Google OAuth)
```

**Pros:**
- ✅ Free SSL
- ✅ No port forwarding
- ✅ Built-in authentication (Cloudflare Access)
- ✅ DDoS protection
- ✅ Keep data on-premise

**Cons:**
- ⚠️ Requires domain name
- ⚠️ Setup complexity

### Option 4: Snapshot Sharing

Share static snapshots instead of live dashboard.

```bash
# In Grafana UI:
# 1. Open dashboard
# 2. Share → Snapshot
# 3. Set expiration time
# 4. Publish to snapshot.raintank.io or self-hosted

# Or use Grafana Image Renderer
docker run -d -p 8081:8081 grafana/grafana-image-renderer

# Configure in Grafana:
# Configuration → External Image Storage
```

**Pros:**
- ✅ No live data exposure
- ✅ Time-limited sharing
- ✅ Point-in-time metrics

**Cons:**
- ❌ Not real-time
- ❌ Manual updates needed

---

## 🛠️ Advanced Configuration

### Custom Metrics

Add custom metrics to `src/eleanor/monitoring/prometheus_metrics.py`:

```python
# Example: Track specific DEX pairs
self.eth_usdc_spread = Gauge(
    'arbitrage_eth_usdc_spread',
    'Current spread for ETH/USDC across DEXs'
)

# Record in orchestrator
self.metrics.eth_usdc_spread.set(spread_pct)
```

### Alerting with Prometheus

Create `monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: trading_alerts
    interval: 30s
    rules:
      - alert: LowCapital
        expr: arbitrage_capital_usd < 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Trading capital below $10k"

      - alert: HighErrorRate
        expr: rate(arbitrage_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

### Telegram Notifications

```python
# Add to orchestrator
import requests

def send_telegram_alert(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={
        'chat_id': chat_id,
        'text': message
    })

# Call on important events
if total_profit > 1000:
    send_telegram_alert(f"🎉 Milestone: $1000 profit reached!")
```

---

## 📊 Metrics Reference

### Trading Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `arbitrage_trades_total` | Counter | Total trades (labels: status, priority) |
| `arbitrage_profit_usd_total` | Counter | Total profit in USD |
| `arbitrage_capital_usd` | Gauge | Current trading capital |
| `arbitrage_trade_size_usd` | Histogram | Trade size distribution |
| `arbitrage_profit_pct` | Histogram | Profit percentage distribution |

### Scraping Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `arbitrage_scrape_duration_seconds` | Histogram | Time to scrape all DEXs |
| `arbitrage_pairs_scraped` | Gauge | Number of pairs scraped |
| `arbitrage_dex_prices_total` | Counter | DEX price points collected (label: dex) |

### AI Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `arbitrage_signals_generated_total` | Counter | AI signals (label: priority) |
| `arbitrage_ai_confidence` | Histogram | Confidence score distribution |
| `arbitrage_ai_risk_score` | Histogram | Risk score distribution |

### Performance Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `arbitrage_win_rate` | Gauge | Win rate (0.0-1.0) |
| `arbitrage_total_return_pct` | Gauge | Total return percentage |
| `arbitrage_sharpe_ratio` | Gauge | Sharpe ratio |
| `arbitrage_uptime_seconds` | Gauge | Total uptime |

---

## 🐛 Troubleshooting

### Metrics Not Showing

```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# If connection refused:
docker logs eleanor-arbitrage

# Check if orchestrator is running with metrics enabled
docker exec eleanor-arbitrage ps aux | grep python
```

### Grafana Shows "No Data"

```bash
# Check Prometheus is scraping
# Open http://localhost:9090/targets
# Status should be "UP" for eleanor-arbitrage

# Check Prometheus query
# Try: arbitrage_capital_usd

# Check dashboard data source
# Grafana → Configuration → Data Sources
# Test connection to Prometheus
```

### Permission Denied Errors

```bash
# Fix Docker volume permissions
sudo chown -R 472:472 monitoring/grafana/data
sudo chown -R 65534:65534 monitoring/prometheus/data
```

### High Memory Usage

```bash
# Reduce Prometheus retention
# Edit docker-compose.monitoring.yml:
- '--storage.tsdb.retention.time=7d'  # Instead of 30d

# Limit scrape frequency
# Edit monitoring/prometheus/prometheus.yml:
scrape_interval: 30s  # Instead of 15s
```

---

## 📚 Additional Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Dashboard Gallery**: https://grafana.com/grafana/dashboards/

---

## 🔐 Privacy Best Practices

1. **Never expose metrics publicly** without authentication
2. **Use VPN** when accessing remote dashboards
3. **Rotate credentials** regularly
4. **Monitor access logs** for suspicious activity
5. **Keep dashboard snapshots private** or time-limited
6. **Consider data retention** - shorter is more private
7. **Use Grafana Cloud with caution** - understand their data policies

---

## 📝 Next Steps

1. ✅ Start monitoring stack locally
2. ✅ Change default passwords
3. ✅ Access Grafana dashboard at http://localhost:3000
4. ✅ Run paper trading and watch metrics
5. ⬜ Set up alerts for important events
6. ⬜ Decide on public dashboard strategy
7. ⬜ Configure backups for Grafana dashboards
8. ⬜ Enable Prometheus long-term storage (optional)

---

**Questions?** Open an issue on [GitHub](https://github.com/Devon-ODell/EleanorPlatform/issues)
