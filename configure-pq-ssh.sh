#!/bin/bash
# Configure Post-Quantum SSH Encryption
# Implements sntrup761x25519 hybrid key exchange for quantum resistance

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Eleanor Platform - Post-Quantum SSH Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Check OpenSSH version
echo -e "${BLUE}[1/5] Checking OpenSSH version...${NC}"
SSH_VERSION=$(ssh -V 2>&1 | grep -oP 'OpenSSH_\K[0-9.]+')
echo -e "  Current version: OpenSSH_${SSH_VERSION}"

# Check if version supports PQ
REQUIRED_VERSION="9.0"
if awk "BEGIN {exit !($SSH_VERSION >= $REQUIRED_VERSION)}"; then
    echo -e "${GREEN}✓ OpenSSH version supports post-quantum cryptography${NC}"
    NEEDS_UPGRADE=false
else
    echo -e "${YELLOW}⚠️  OpenSSH ${SSH_VERSION} detected. Recommended: ${REQUIRED_VERSION}+${NC}"
    echo -e "${YELLOW}   Post-quantum support may be limited.${NC}"
    NEEDS_UPGRADE=true

    read -p "Do you want to compile OpenSSH 9.6 from source? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Continuing with current version...${NC}"
        NEEDS_UPGRADE=false
    fi
fi

# Upgrade OpenSSH if needed
if [ "$NEEDS_UPGRADE" = true ]; then
    echo -e "${BLUE}[2/5] Compiling OpenSSH 9.6p1 from source...${NC}"

    # Install build dependencies
    apt-get update -qq
    apt-get install -y -qq build-essential libssl-dev zlib1g-dev libpam0g-dev

    # Download
    cd /tmp
    wget -q https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-9.6p1.tar.gz
    tar xzf openssh-9.6p1.tar.gz
    cd openssh-9.6p1

    # Configure and compile
    echo -e "${BLUE}  Configuring...${NC}"
    ./configure --with-pam --with-systemd --prefix=/usr --sysconfdir=/etc/ssh > /dev/null

    echo -e "${BLUE}  Compiling (this may take 5-10 minutes on Pi)...${NC}"
    make -j$(nproc) > /dev/null

    echo -e "${BLUE}  Installing...${NC}"
    make install > /dev/null

    echo -e "${GREEN}✓ OpenSSH 9.6p1 installed${NC}"

    # Verify
    /usr/sbin/sshd -V 2>&1 | head -1
else
    echo -e "${BLUE}[2/5] Skipping OpenSSH upgrade${NC}"
fi

# Backup existing SSH config
echo -e "${BLUE}[3/5] Backing up SSH configuration...${NC}"
BACKUP_DIR="/etc/ssh/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /etc/ssh/sshd_config "$BACKUP_DIR/"
cp /etc/ssh/ssh_config "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"

# Generate Ed25519 host key if not exists
echo -e "${BLUE}[4/5] Configuring host keys...${NC}"
if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
    echo -e "${BLUE}  Generating Ed25519 host key...${NC}"
    ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N "" > /dev/null
    echo -e "${GREEN}✓ Ed25519 host key generated${NC}"
else
    echo -e "${GREEN}✓ Ed25519 host key already exists${NC}"
fi

# Configure sshd_config for post-quantum
echo -e "${BLUE}[5/5] Configuring post-quantum key exchange...${NC}"

# Create new sshd_config with PQ settings
cat > /etc/ssh/sshd_config <<EOF
# Eleanor Platform - Post-Quantum SSH Configuration
# Generated: $(date)

# ============================================
# POST-QUANTUM CRYPTOGRAPHY
# ============================================

# Hybrid post-quantum key exchange (classical + PQ)
# sntrup761x25519: Streamlined NTRU Prime + X25519
KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org

# Ed25519 host keys (quantum-resistant, small key size)
HostKey /etc/ssh/ssh_host_ed25519_key

# Only accept Ed25519 public keys
PubkeyAcceptedAlgorithms ssh-ed25519,ssh-ed25519-cert-v01@openssh.com

# Strong ciphers (AES-256 for PQ readiness)
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes256-ctr

# Strong MACs
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# ============================================
# SECURITY HARDENING
# ============================================

# Authentication
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
UsePAM yes

# Rate limiting
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 30

# Network
AddressFamily any
Port 22
ListenAddress 0.0.0.0

# Session management
ClientAliveInterval 300
ClientAliveCountMax 2
TCPKeepAlive yes

# Disable insecure features
X11Forwarding no
PrintMotd no
PrintLastLog yes
PermitTunnel no
PermitUserEnvironment no
GatewayPorts no
AllowAgentForwarding yes
AllowTcpForwarding yes

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Environment
AcceptEnv LANG LC_*

# Subsystems
Subsystem sftp /usr/lib/openssh/sftp-server

# ============================================
# PERFORMANCE (Raspberry Pi optimized)
# ============================================

# Compression (helpful for Pi)
Compression yes

# Keep connections alive
UseDNS no
EOF

echo -e "${GREEN}✓ Post-quantum SSH configuration applied${NC}"

# Test configuration
echo
echo -e "${BLUE}Testing SSH configuration...${NC}"
if sshd -t; then
    echo -e "${GREEN}✓ Configuration syntax is valid${NC}"
else
    echo -e "${RED}❌ Configuration has errors!${NC}"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp "$BACKUP_DIR/sshd_config" /etc/ssh/sshd_config
    exit 1
fi

# Restart SSH service
echo
echo -e "${BLUE}Restarting SSH service...${NC}"
systemctl restart sshd

if systemctl is-active --quiet sshd; then
    echo -e "${GREEN}✓ SSH service restarted successfully${NC}"
else
    echo -e "${RED}❌ SSH service failed to start!${NC}"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp "$BACKUP_DIR/sshd_config" /etc/ssh/sshd_config
    systemctl restart sshd
    exit 1
fi

# Configure client-side (for current user)
echo
echo -e "${BLUE}Configuring SSH client for current user...${NC}"

CURRENT_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$CURRENT_USER)
mkdir -p "$USER_HOME/.ssh"

cat > "$USER_HOME/.ssh/config" <<EOF
# Eleanor Platform - Post-Quantum SSH Client Configuration

# Default settings for all hosts
Host *
    # Post-quantum key exchange
    KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256

    # Prefer Ed25519 keys
    IdentityFile ~/.ssh/id_ed25519
    PubkeyAcceptedAlgorithms ssh-ed25519

    # Strong ciphers and MACs
    Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
    MACs hmac-sha2-512-etm@openssh.com

    # Security
    HashKnownHosts yes
    VerifyHostKeyDNS yes
    StrictHostKeyChecking ask

    # Performance
    Compression yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

chown -R $CURRENT_USER:$CURRENT_USER "$USER_HOME/.ssh"
chmod 600 "$USER_HOME/.ssh/config"

echo -e "${GREEN}✓ SSH client configured${NC}"

# Generate Ed25519 key if needed
if [ ! -f "$USER_HOME/.ssh/id_ed25519" ]; then
    echo
    echo -e "${BLUE}Generating Ed25519 SSH key for $CURRENT_USER...${NC}"
    sudo -u $CURRENT_USER ssh-keygen -t ed25519 -f "$USER_HOME/.ssh/id_ed25519" -C "eleanor-pi-pq-$(date +%Y%m%d)"
    echo -e "${GREEN}✓ Ed25519 key generated${NC}"
fi

# Show public key
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Post-Quantum SSH Configuration Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${GREEN}Key Exchange Algorithm:${NC}"
echo -e "  ${BLUE}sntrup761x25519-sha512@openssh.com${NC}"
echo -e "  (Hybrid: NTRU Prime + Curve25519)"
echo
echo -e "${GREEN}Your Ed25519 Public Key:${NC}"
cat "$USER_HOME/.ssh/id_ed25519.pub"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Copy public key to remote machines:"
echo -e "     ${BLUE}ssh-copy-id -i ~/.ssh/id_ed25519.pub user@remote${NC}"
echo
echo -e "  2. Test PQ key exchange:"
echo -e "     ${BLUE}ssh -v user@remote 2>&1 | grep 'kex:'${NC}"
echo -e "     Should show: ${GREEN}sntrup761x25519-sha512@openssh.com${NC}"
echo
echo -e "  3. For remote access, install Tailscale:"
echo -e "     ${BLUE}curl -fsSL https://tailscale.com/install.sh | sh${NC}"
echo
echo -e "${GREEN}Security Notes:${NC}"
echo -e "  ✅ Post-quantum protection against future quantum computers"
echo -e "  ✅ Hybrid approach: secure even if PQ algorithm is broken"
echo -e "  ✅ Password authentication disabled (keys only)"
echo -e "  ✅ Rate limiting enabled"
echo
echo -e "${YELLOW}Backup Location:${NC} $BACKUP_DIR"
echo
