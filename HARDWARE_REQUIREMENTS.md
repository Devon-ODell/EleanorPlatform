# Eleanor Platform - Hardware Requirements for Maximum Privacy
## Qubes OS + Mullvad VPN + Intel ME Disabled

## Overview

For running Eleanor Platform with maximum privacy protection against Five Eyes surveillance, you need:
1. **Hardware capable of running Qubes OS smoothly**
2. **Motherboard with Intel ME disabled or neutralized**
3. **Sufficient resources for multiple VMs**
4. **Optional: Coreboot/Libreboot compatibility**

---

## System Requirements

### Minimum (Paper Trading Only)
- **CPU**: 4 cores / 8 threads (Intel i5-8400 or AMD Ryzen 5 2600)
- **RAM**: 16GB DDR4
- **Storage**: 250GB SSD
- **Use Case**: Basic paper trading, 2-3 qubes running

### Recommended (Full Production)
- **CPU**: 6+ cores / 12+ threads (Intel i7-10700K or AMD Ryzen 7 5800X)
- **RAM**: 32GB DDR4
- **Storage**: 512GB NVMe SSD
- **Use Case**: Live trading with multiple strategies, 5-8 qubes

### Optimal (High-Volume Trading)
- **CPU**: 8+ cores / 16+ threads (Intel i9-12900K or AMD Ryzen 9 5950X)
- **RAM**: 64GB DDR4/DDR5
- **Storage**: 1TB NVMe SSD + 2TB HDD for backups
- **Use Case**: Multiple live strategies, extensive backtesting, 10+ qubes

---

## Intel Management Engine (ME) - The Five Eyes Threat

### What is Intel ME?

**Intel Management Engine (ME)** is a separate processor embedded in Intel chipsets since 2006:
- Runs independently of the main CPU
- Has full access to system memory, network, USB
- Cannot be disabled through normal BIOS settings
- Runs even when system is "off" (if plugged in)
- Has been exploited by government agencies (NSA, GCHQ, etc.)

**Why It's Dangerous:**
- Remote access capability (AMT - Active Management Technology)
- Can bypass OS-level security
- Firmware updates can be pushed remotely
- Part of Five Eyes surveillance infrastructure
- Cannot be audited (proprietary, signed firmware)

**Known Exploits:**
- CVE-2017-5689: Remote execution flaw
- CVE-2018-3658: Privilege escalation
- NSA ANT catalog mentions ME as attack vector

### ME Neutralization Options

**Option 1: ME Cleaner (Partial Disable)**
- Removes most ME modules except minimum required for boot
- Works on most Intel platforms (Sandy Bridge to Coffee Lake)
- Requires SPI programmer to flash modified firmware
- ~95% of ME code removed

**Option 2: Full ME Disable (Coreboot/Libreboot)**
- Complete removal of ME blob
- Requires Coreboot/Libreboot compatible hardware
- 100% ME removal
- Limited hardware compatibility

**Option 3: AMD Platform**
- AMD has PSP (Platform Security Processor) instead
- Similar concerns but less documented exploits
- Easier to neutralize on some platforms

---

## Recommended Motherboards with Removable BIOS Chip

### Best for ME Neutralization (Intel)

#### 1. **ASUS KGPE-D16** ⭐ (BEST OPTION)
**Why:** Libreboot compatible, no ME at all (pre-ME era)
- **CPU**: Dual AMD Opteron 6200/6300 series
- **RAM**: Up to 256GB ECC DDR3
- **BIOS**: Socketed SOIC-16 chip (easily removable)
- **Status**: 100% free firmware (Libreboot)
- **Pros**:
  - No ME/PSP at all
  - Full Libreboot support
  - ECC memory support
  - Extremely stable for 24/7 operation
- **Cons**:
  - Older platform (2012)
  - Higher power consumption
  - Harder to find
- **Price**: $200-400 used
- **Availability**: eBay, server surplus sellers

#### 2. **ASUS KCMA-D8**
**Why:** Libreboot compatible, smaller than KGPE-D16
- **CPU**: AMD Opteron 4200/4300 series
- **RAM**: Up to 64GB ECC DDR3
- **BIOS**: Socketed SOIC-8 chip
- **Status**: 100% free firmware (Libreboot)
- **Price**: $150-300 used

#### 3. **ThinkPad X200/T400** (Laptop Alternative)
**Why:** Complete Libreboot support, portable
- **CPU**: Intel Core 2 Duo (pre-ME)
- **RAM**: Up to 8GB DDR3
- **BIOS**: Easily flashable
- **Status**: 100% Libreboot
- **Use Case**: Mobile trading, low power
- **Price**: $100-200 used

### Modern Platforms with ME_cleaner Support

#### 4. **Gigabyte Z390 AORUS PRO** ⭐ (Modern Option)
**Why:** Socketed BIOS chip, good ME_cleaner support
- **CPU**: Intel 8th/9th Gen (i7-9700K, i9-9900K)
- **RAM**: Up to 128GB DDR4
- **BIOS**: Dual BIOS chips, SOIC-8 socketed
- **ME**: Can be neutralized with ME_cleaner
- **Pros**:
  - Modern platform (good performance)
  - Dual BIOS (backup protection)
  - Easy BIOS chip access
  - Good Qubes OS compatibility
- **Cons**:
  - Requires ME_cleaner (not 100% removal)
  - Still has ME hardware present
- **Price**: $150-250 used
- **Availability**: Common on used market

#### 5. **ASUS ROG Maximus XI Hero (Z390)**
**Why:** Socketed BIOS, excellent build quality
- **CPU**: Intel 8th/9th Gen
- **RAM**: Up to 128GB DDR4
- **BIOS**: SOIC-8 socketed (under heatsink)
- **ME**: ME_cleaner compatible
- **Price**: $200-350 used

#### 6. **ASRock Z370 Pro4**
**Why**: Budget option with socketed BIOS
- **CPU**: Intel 8th/9th Gen
- **RAM**: Up to 64GB DDR4
- **BIOS**: SOIC-8 socketed
- **ME**: ME_cleaner compatible
- **Price**: $80-150 used

### AMD Platforms (PSP Alternative)

#### 7. **ASUS ROG Crosshair VIII Hero (X570)**
**Why:** Modern AMD, PSP less intrusive than ME
- **CPU**: AMD Ryzen 3000/5000 series
- **RAM**: Up to 128GB DDR4
- **BIOS**: SOIC-8 socketed
- **PSP**: Less documented surveillance risk than Intel ME
- **Pros**:
  - Excellent performance
  - Lower power than Intel
  - Good Qubes support (IOMMU)
- **Cons**:
  - PSP still present (harder to neutralize than ME)
- **Price**: $250-400

#### 8. **ASUS PRIME X570-PRO**
**Why:** Business-class, good stability
- **CPU**: AMD Ryzen 3000/5000
- **RAM**: Up to 128GB DDR4
- **BIOS**: Socketed SOIC-8
- **Price**: $150-250

---

## BIOS Chip Types and Removal

### Common BIOS Chip Formats

**SOIC-8 (Small Outline IC, 8-pin)**
- Most common on modern motherboards
- 8mm x 6mm package
- Removable with SOIC-8 clip or hot air rework
- Easy to read/write with CH341A programmer

**SOIC-16 (16-pin)**
- Found on some server boards
- Larger, easier to work with
- Used on ASUS KGPE-D16

**DIP-8 (Dual Inline Package)**
- Older format, very easy to remove
- Through-hole socket
- Can be removed without soldering

### How to Identify Removable BIOS

**Look for:**
1. **Socket/holder** - Some boards have BIOS in a socket
2. **Chip labeling** - Usually says "BIOS" or manufacturer (Winbond, Macronix)
3. **Location** - Often near I/O shield or PCH chipset
4. **Accessibility** - Should not be under heatsinks (or easily accessible)

**Common BIOS Chip Manufacturers:**
- Winbond (W25Q series) - Very common
- Macronix (MX25L series)
- GigaDevice (GD25 series)

---

## ME Neutralization Process

### Method 1: ME_cleaner (for Modern Intel)

**Requirements:**
- CH341A USB programmer ($5-15 on AliExpress/Amazon)
- SOIC-8 test clip ($3-5)
- Python 3 installed on a Linux system
- Target motherboard with Intel ME

**Steps:**

1. **Extract Current BIOS:**
```bash
# Using flashrom
sudo apt install flashrom
sudo flashrom -p ch341a_spi -r bios_backup.bin

# Verify by reading again
sudo flashrom -p ch341a_spi -r bios_backup2.bin
sha256sum bios_backup.bin bios_backup2.bin
# Must match!
```

2. **Clean ME:**
```bash
# Clone ME_cleaner
git clone https://github.com/corna/me_cleaner.git
cd me_cleaner

# Run ME_cleaner
python3 me_cleaner.py -S -O bios_cleaned.bin ../bios_backup.bin

# -S: Soft disable (safest)
# -O: Output file
```

3. **Flash Cleaned BIOS:**
```bash
sudo flashrom -p ch341a_spi -w bios_cleaned.bin
```

4. **Verify ME Status:**
```bash
# After booting
sudo apt install intelmetool
sudo intelmetool -m
# Should show ME disabled or minimal
```

### Method 2: Libreboot (for Compatible Hardware)

**Supported Hardware:**
- ASUS KGPE-D16 (recommended)
- ASUS KCMA-D8
- ThinkPad X200, T400, X60, T60

**Process:**
```bash
# Download Libreboot
wget https://mirrors.mit.edu/libreboot/stable/20160907/libreboot_r20160907_util.tar.xz
tar -xf libreboot_r20160907_util.tar.xz

# Flash (varies by board)
cd libreboot_r20160907_util
sudo ./flash update path/to/libreboot.rom
```

---

## Complete Hardware Build Recommendations

### Build 1: Maximum Privacy (Libreboot)
**Best for: Absolute paranoia, Five Eyes protection**

| Component | Model | Price | Notes |
|-----------|-------|-------|-------|
| Motherboard | ASUS KGPE-D16 | $300 | 100% free firmware |
| CPU | 2x AMD Opteron 6380 (16-core) | $100 | 32 cores total |
| RAM | 128GB ECC DDR3 (8x16GB) | $200 | ECC for stability |
| Storage | 1TB Samsung 870 EVO | $80 | Fast, reliable |
| PSU | EVGA 750W 80+ Gold | $100 | Dual CPU needs power |
| Case | Fractal Define R5 | $100 | Quiet, good airflow |
| Cooling | 2x Noctua NH-D9L | $100 | Dual CPU coolers |
| **TOTAL** | | **~$980** | 100% ME-free |

**Performance:**
- 32 cores = 20+ qubes smoothly
- ECC RAM = maximum stability
- 24/7 operation ready
- Zero Intel ME risk

### Build 2: Modern Performance (ME_cleaner)
**Best for: High performance, good privacy**

| Component | Model | Price | Notes |
|-----------|-------|-------|-------|
| Motherboard | Gigabyte Z390 AORUS PRO | $200 | Socketed BIOS |
| CPU | Intel i9-9900K | $300 | 8C/16T, excellent perf |
| RAM | 64GB DDR4-3200 (4x16GB) | $180 | Fast, plenty for qubes |
| Storage | 1TB Samsung 980 PRO | $120 | NVMe speed |
| GPU | Intel integrated | $0 | Good enough for trading |
| PSU | Corsair RM750x | $120 | Quiet, reliable |
| Case | Fractal Meshify C | $90 | Good airflow |
| Cooling | Noctua NH-D15 | $100 | Quiet, powerful |
| **TOTAL** | | **~$1,110** | ME neutralized |

**Performance:**
- 8C/16T = excellent for Qubes
- Fast NVMe storage
- Quiet operation
- Modern platform

### Build 3: AMD Budget (No Intel ME)
**Best for: Budget-conscious, avoid Intel entirely**

| Component | Model | Price | Notes |
|-----------|-------|-------|-------|
| Motherboard | ASUS PRIME X570-P | $150 | Socketed BIOS |
| CPU | AMD Ryzen 7 5700X | $200 | 8C/16T, efficient |
| RAM | 32GB DDR4-3200 (2x16GB) | $80 | Good for 8+ qubes |
| Storage | 512GB WD SN570 | $50 | Budget NVMe |
| GPU | AMD integrated | $0 | Needs 5700G instead |
| PSU | Corsair CX650M | $70 | Reliable |
| Case | Cooler Master Q300L | $50 | Compact, cheap |
| Cooling | Stock AMD cooler | $0 | Adequate |
| **TOTAL** | | **~$600** | No Intel ME |

**Performance:**
- Good performance/dollar
- AMD PSP less intrusive
- Low power consumption

### Build 4: Portable Privacy (Laptop)
**Best for: Mobile trading, travel**

| Component | Model | Price | Notes |
|-----------|-------|-------|-------|
| Laptop | ThinkPad X200 | $150 | Libreboot compatible |
| RAM Upgrade | 8GB DDR3 (2x4GB) | $30 | Max for X200 |
| Storage | 512GB SATA SSD | $50 | Upgrade from HDD |
| Battery | Extended 9-cell | $40 | Longer runtime |
| **TOTAL** | | **~$270** | Fully portable |

**Performance:**
- 100% Libreboot
- Portable for travel
- Low power draw
- Limited to 3-4 qubes

---

## Additional Security Hardware

### 1. Hardware Security Key
**YubiKey 5 NFC** ($50)
- U2F/FIDO2 for 2FA
- GPG key storage
- Works with Qubes OS

### 2. Hardware Entropy Source
**OneRNG** ($50) or **TrueRNG** ($50)
- Hardware random number generator
- Better than CPU RNG
- Important for crypto key generation

### 3. Air-Gapped Backup System
**Raspberry Pi 4** ($75) + **USB drives** ($50)
- Offline backup system
- No network connection
- Store vault qube backups

### 4. Faraday Bag
**Mission Darkness Faraday Bag** ($30-80)
- Blocks all RF signals
- Store hardware wallet/keys
- Prevents remote attacks

### 5. UPS (Uninterruptible Power Supply)
**APC Back-UPS 1500VA** ($200)
- Prevents data loss
- Clean power for stability
- Important for 24/7 trading

---

## Shopping List Summary

### Option A: Maximum Privacy (Libreboot)
- **Cost**: ~$980 (desktop) or ~$270 (laptop)
- **Privacy**: 100% (no ME/PSP)
- **Performance**: Excellent (desktop) / Basic (laptop)

### Option B: Modern Performance (ME_cleaner)
- **Cost**: ~$1,110
- **Privacy**: 95% (ME neutralized)
- **Performance**: Excellent

### Option C: AMD Budget
- **Cost**: ~$600
- **Privacy**: 90% (avoid Intel ME)
- **Performance**: Good

### Tools Required for ME Removal
- CH341A USB Programmer: $15
- SOIC-8 Test Clip: $5
- Jumper wires (if needed): $3
- **Total**: ~$25

---

## Where to Buy

### New Components
- **Newegg**: Good for motherboards/CPUs
- **Amazon**: Fast shipping, easy returns
- **B&H Photo**: No tax in some states

### Used/Server Hardware
- **eBay**: ASUS KGPE-D16, Opteron CPUs
- **LabGopher**: Server surplus search
- **ServeTheHome Forums**: Homelab community
- **r/homelabsales**: Reddit marketplace

### Tools & Programmers
- **AliExpress**: CH341A programmer (cheap, slow shipping)
- **Amazon**: Same but faster, more expensive

### Privacy Hardware
- **Yubico.com**: YubiKeys (official)
- **System76**: Coreboot laptops (new)
- **Purism**: Librem laptops (expensive but free firmware)

---

## Performance Benchmarks

### Qubes OS Resource Usage (Estimated)

**dom0**: 2GB RAM, 1 CPU core
**sys-vpn**: 512MB RAM, 0.5 CPU core
**sys-firewall**: 512MB RAM, 0.5 CPU core
**trading-qube**: 4GB RAM, 2 CPU cores
**vault**: 1GB RAM, 0.5 CPU core
**Multiple strategies**: +2GB RAM, +1 CPU per qube

**Recommended Allocation:**
- 16GB RAM: 3-4 qubes (basic paper trading)
- 32GB RAM: 6-8 qubes (live trading)
- 64GB RAM: 10+ qubes (multiple strategies + backtesting)

### Expected Performance

**ASUS KGPE-D16 (32 cores, 128GB):**
- Simultaneous qubes: 20+
- Backtest speed: ~5-10 min for 3 months
- Paper trading: 50+ concurrent strategies
- Live trading: 10+ concurrent bots

**Gigabyte Z390 (8C/16T, 64GB):**
- Simultaneous qubes: 10-12
- Backtest speed: ~10-15 min for 3 months
- Paper trading: 20 concurrent strategies
- Live trading: 5-8 concurrent bots

**AMD Ryzen 7 5700X (8C/16T, 32GB):**
- Simultaneous qubes: 8-10
- Backtest speed: ~8-12 min for 3 months
- Paper trading: 10-15 concurrent strategies
- Live trading: 3-5 concurrent bots

---

## Setup Priority Checklist

1. ✅ Purchase hardware with removable BIOS chip
2. ✅ Buy CH341A programmer + SOIC-8 clip
3. ✅ Backup original BIOS (3 copies!)
4. ✅ Flash ME_cleaner or Libreboot
5. ✅ Install Qubes OS
6. ✅ Set up Mullvad VPN in sys-vpn
7. ✅ Create trading-qube
8. ✅ Deploy Eleanor Platform
9. ✅ Test with paper trading
10. ✅ Go live with small capital

---

## Final Recommendations

### For Maximum Privacy (Five Eyes Protection):
**Buy**: ASUS KGPE-D16 + dual Opteron 6380
**Why**: 100% free firmware, no ME, no PSP, no backdoors
**Cost**: ~$980
**Performance**: Excellent for trading bots

### For Modern Performance + Good Privacy:
**Buy**: Gigabyte Z390 AORUS PRO + i9-9900K
**Why**: Fast, good Qubes support, ME_cleaner works well
**Cost**: ~$1,110
**Performance**: Excellent all-around

### For Budget + Avoiding Intel:
**Buy**: ASUS PRIME X570-P + Ryzen 7 5700X
**Why**: No Intel ME, good performance, affordable
**Cost**: ~$600
**Performance**: Good for starting out

### For Portable/Travel:
**Buy**: ThinkPad X200 + Libreboot
**Why**: 100% free firmware, portable, proven
**Cost**: ~$270
**Performance**: Basic but secure

---

**⚠️ IMPORTANT SECURITY NOTES:**

1. **Always backup original BIOS 3 times** before flashing
2. **Test with multimeter** to avoid bricking ($5 investment)
3. **Never flash BIOS with system powered on**
4. **Keep CH341A programmer** for recovery
5. **Document everything** for troubleshooting

**Privacy is not paranoia when facing state-level adversaries. The Five Eyes surveillance apparatus is real, and ME is a documented attack vector.**
