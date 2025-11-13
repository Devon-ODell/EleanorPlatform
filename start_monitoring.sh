#!/bin/bash
# Quick Start Monitoring Stack
# Starts Prometheus + Grafana + Arbitrage Bot

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Eleanor Platform - Monitoring Stack Startup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo -e "${YELLOW}Install Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo -e "${BLUE}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and change default passwords!${NC}"
    echo -e "${YELLOW}   Run: nano .env${NC}"
    echo
    read -p "Press Enter to continue with default settings (NOT RECOMMENDED for production) or Ctrl+C to exit and edit .env first..."
fi

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p data/arbitrage
mkdir -p logs
mkdir -p monitoring/prometheus/data
mkdir -p monitoring/grafana/data

# Set correct permissions for Grafana
echo -e "${BLUE}Setting permissions...${NC}"
sudo chown -R 472:472 monitoring/grafana/data 2>/dev/null || true
sudo chown -R 65534:65534 monitoring/prometheus/data 2>/dev/null || true

# Pull images
echo -e "${BLUE}Pulling Docker images...${NC}"
docker-compose -f docker-compose.monitoring.yml pull

# Start services
echo -e "${BLUE}Starting monitoring stack...${NC}"
docker-compose -f docker-compose.monitoring.yml up -d

echo
echo -e "${GREEN}✅ Monitoring stack started successfully!${NC}"
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Access Points:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "  📊 ${GREEN}Grafana Dashboard:${NC}  http://localhost:3000"
echo -e "     ${YELLOW}Default login:${NC} admin / eleanor2025"
echo
echo -e "  🔍 ${GREEN}Prometheus:${NC}         http://localhost:9090"
echo
echo -e "  📈 ${GREEN}Metrics Endpoint:${NC}   http://localhost:8000/metrics"
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check service status
echo -e "${BLUE}Service Status:${NC}"
docker-compose -f docker-compose.monitoring.yml ps

echo
echo -e "${YELLOW}📝 Useful Commands:${NC}"
echo
echo -e "  View logs:           ${GREEN}docker-compose -f docker-compose.monitoring.yml logs -f${NC}"
echo -e "  Stop services:       ${GREEN}docker-compose -f docker-compose.monitoring.yml down${NC}"
echo -e "  Restart services:    ${GREEN}docker-compose -f docker-compose.monitoring.yml restart${NC}"
echo
echo -e "${YELLOW}⚠️  Security Reminder:${NC}"
echo -e "  1. Change default Grafana password immediately!"
echo -e "  2. Edit .env file with strong passwords"
echo -e "  3. Keep metrics endpoint (port 8000) firewalled"
echo
echo -e "${GREEN}Happy Trading! 🚀${NC}"
