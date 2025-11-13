# Intel ME Neutralization Guide
## Complete Step-by-Step Tutorial for Removing the Five Eyes Backdoor

## ⚠️ WARNING

**This procedure can BRICK your motherboard if done incorrectly.**
- Always make 3+ backups of original BIOS
- Test your setup with a multimeter
- Have a recovery plan
- Understand the risks

**This guide is for educational and privacy purposes only.**

---

## What You'll Need

### Hardware
- ✅ CH341A USB BIOS programmer ($10-15)
- ✅ SOIC-8 test clip with ribbon cable ($5-10)
- ✅ Target motherboard with Intel chipset
- ✅ Second computer running Linux (for flashing)
- ✅ (Optional) Multimeter for testing

### Software
- ✅ Linux system (Ubuntu/Debian recommended)
- ✅ Flashrom
- ✅ ME_cleaner
- ✅ Python 3
- ✅ Git

### Shopping Links
**Amazon (Fast):**
- CH341A Programmer: Search "CH341A USB programmer"
- SOIC-8 Clip: Search "SOIC-8 test clip"
- ~$20-30 total

**AliExpress (Cheap):**
- Same items, ~$8-15 total, 2-4 week shipping

---

## Part 1: Identify Your BIOS Chip

### Step 1: Locate the BIOS Chip

**Common Locations:**
1. Near the PCH (Platform Controller Hub) chipset
2. Near the I/O shield
3. Under heatsinks (need to remove)
4. Near the 24-pin ATX power connector

**What to Look For:**
- Small 8-pin chip (SOIC-8 package)
- Usually labeled: "BIOS", "25", or manufacturer name
- 8mm x 6mm size
- Often has a small dot/circle indicating pin 1

**Common BIOS Chip Markings:**
- Winbond 25Q128FV (16MB)
- Winbond 25Q64FV (8MB)
- Macronix MX25L6406E (8MB)
- GigaDevice GD25B64 (8MB)

### Step 2: Identify Pin 1

**Pin 1 Indicators:**
- Small dot or circle on chip
- Notch on one corner
- Pin 1 is usually nearest to a visible marking

**Pin Layout (SOIC-8):**
```
        ___
  Pin 1 o| |o Pin 8
  Pin 2  | |  Pin 7
  Pin 3  | |  Pin 6
  Pin 4  |_|  Pin 5

Pin 1: CS (Chip Select)
Pin 2: MISO (Data Out)
Pin 3: WP (Write Protect) - must be HIGH
Pin 4: GND
Pin 5: MOSI (Data In)
Pin 6: CLK (Clock)
Pin 7: HOLD - must be HIGH
Pin 8: VCC (3.3V)
```

### Step 3: Document Everything

**Take Photos:**
- Wide shot showing chip location on board
- Close-up of chip showing pin 1
- Any labels or markings
- Surrounding components

**Write Down:**
- Motherboard model
- BIOS chip part number
- Current BIOS version (from BIOS setup screen)
- Date and your system specs

---

## Part 2: Set Up Your Flashing Environment

### Step 1: Install Required Software

**On your Linux flashing machine:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y build-essential git python3 python3-pip \
    libpci-dev libusb-1.0-0-dev libftdi-dev pciutils usbutils \
    flashrom

# Verify flashrom installation
flashrom --version

# Clone ME_cleaner
cd ~/
git clone https://github.com/corna/me_cleaner.git
cd me_cleaner

# Test ME_cleaner
python3 me_cleaner.py --help
```

### Step 2: Connect CH341A Programmer

**IMPORTANT: Remove ALL power from target motherboard**
- Unplug PSU power cable
- Press power button 5-10 times to discharge capacitors
- Wait 5 minutes
- Double-check with multimeter (0V across pins)

**Connect SOIC-8 Clip:**

1. **Identify Pin 1 on your clip** (usually red wire)
2. **Align clip Pin 1 with chip Pin 1**
3. **Clip onto chip** - should click/grip firmly
4. **Connect ribbon cable to CH341A programmer**
5. **Plug CH341A into USB port of flashing computer**

**Verify Connection:**
```bash
# Check USB device
lsusb | grep CH341
# Should show: "1a86:5512 QinHeng Electronics CH341"

# Test communication
sudo flashrom -p ch341a_spi
# Should detect chip
```

### Step 3: Verify Chip Detection

```bash
sudo flashrom -p ch341a_spi

# Expected output:
# Calibrating delay loop... OK.
# Found Winbond flash chip "W25Q128.V" (16384 kB, SPI) on ch341a_spi.
# No operations were specified.
```

**If chip not detected:**
- Check clip orientation (Pin 1 alignment)
- Ensure clip is firmly attached
- Check for oxidation on chip pins
- Try reseating the clip
- Verify motherboard is completely powered off

---

## Part 3: Backup Original BIOS

**CRITICAL STEP - DO NOT SKIP!**

### Step 1: Read BIOS Three Times

```bash
# Create backup directory
mkdir -p ~/bios_backups
cd ~/bios_backups

# First read
sudo flashrom -p ch341a_spi -r bios_backup_1.bin
# Wait for completion (~2-5 minutes)

# Second read
sudo flashrom -p ch341a_spi -r bios_backup_2.bin

# Third read
sudo flashrom -p ch341a_spi -r bios_backup_3.bin
```

### Step 2: Verify Backups are Identical

```bash
# Calculate checksums
sha256sum bios_backup_*.bin

# All three MUST match exactly!
# Example output:
# a1b2c3d4... bios_backup_1.bin
# a1b2c3d4... bios_backup_2.bin
# a1b2c3d4... bios_backup_3.bin
```

**If checksums don't match:**
- ❌ DO NOT PROCEED
- ❌ Your clip connection is unstable
- Fix: Reseat clip, try again
- You MUST have matching backups!

### Step 3: Store Backups Safely

```bash
# Copy to multiple locations
cp bios_backup_1.bin ~/bios_backup_original.bin
cp bios_backup_1.bin /media/usb_drive/  # USB backup
cp bios_backup_1.bin ~/Dropbox/  # Cloud backup (encrypted!)

# Create checksums file
sha256sum bios_backup_1.bin > CHECKSUM.txt

# Add metadata
echo "Motherboard: $(MOTHERBOARD_MODEL)" >> CHECKSUM.txt
echo "Date: $(date)" >> CHECKSUM.txt
echo "BIOS Version: $(BIOS_VERSION)" >> CHECKSUM.txt
```

**Store backups in:**
1. Original location (~/bios_backups)
2. USB drive (offline backup)
3. Encrypted cloud storage (recovery option)
4. Different physical location (fire/theft protection)

---

## Part 4: Neutralize Intel ME

### Step 1: Analyze Current ME Status

```bash
cd ~/me_cleaner

# Check current ME firmware
python3 me_cleaner.py -c ~/bios_backups/bios_backup_1.bin

# Output shows:
# - ME version
# - ME region location
# - Modules present
# - File system info
```

### Step 2: Clean ME Firmware

**Option A: Soft Disable (Recommended - Safest)**

```bash
python3 me_cleaner.py -S -O ~/bios_backups/bios_cleaned.bin ~/bios_backups/bios_backup_1.bin

# -S: Soft disable (keeps minimum for boot)
# -O: Output file
```

**Option B: Aggressive Cleaning (More Complete)**

```bash
python3 me_cleaner.py -s -r -t -d -O ~/bios_backups/bios_cleaned.bin ~/bios_backups/bios_backup_1.bin

# -s: Soft disable
# -r: Relocate partition
# -t: Truncate ME region
# -d: Descriptor unlock
```

**Option C: Maximum Removal (Risky - May Not Boot)**

```bash
# Only for advanced users!
python3 me_cleaner.py -S -r -t -d -O ~/bios_backups/bios_cleaned.bin ~/bios_backups/bios_backup_1.bin
```

### Step 3: Verify Cleaned BIOS

```bash
# Check cleaned firmware
python3 me_cleaner.py -c ~/bios_backups/bios_cleaned.bin

# Should show:
# "ME is removable/not critical"
# "Flash descriptor is valid"
# "Flash regions are accessible"

# Compare sizes
ls -lh ~/bios_backups/bios_backup_1.bin
ls -lh ~/bios_backups/bios_cleaned.bin
# Cleaned should be same size (ME region filled with 0xFF)
```

---

## Part 5: Flash Cleaned BIOS

### Step 1: Double-Check Everything

**Checklist:**
- ✅ Three identical backup files
- ✅ Backups stored in multiple locations
- ✅ Cleaned BIOS created successfully
- ✅ ME_cleaner reported no errors
- ✅ Clip still firmly attached to chip
- ✅ System completely powered off
- ✅ No other programs accessing CH341A

### Step 2: Flash the Cleaned BIOS

```bash
# POINT OF NO RETURN - Last chance to abort!

# Flash cleaned BIOS
sudo flashrom -p ch341a_spi -w ~/bios_backups/bios_cleaned.bin

# This will:
# 1. Erase chip (~30 seconds)
# 2. Write new firmware (~2-5 minutes)
# 3. Verify (~2-5 minutes)

# DO NOT INTERRUPT THIS PROCESS!
# - Don't touch the clip
# - Don't unplug USB
# - Don't power on system
# - Don't close terminal
```

**Expected Output:**
```
Reading old flash chip contents... done.
Erasing and writing flash chip... Erase/write done.
Verifying flash... VERIFIED.
```

### Step 3: Verify Flash Success

```bash
# Read back flashed BIOS
sudo flashrom -p ch341a_spi -r ~/bios_backups/bios_verify.bin

# Compare with what we flashed
sha256sum ~/bios_backups/bios_cleaned.bin ~/bios_backups/bios_verify.bin

# MUST MATCH!
```

---

## Part 6: Test the System

### Step 1: Remove Clip and Reconnect Power

```bash
# Carefully remove SOIC-8 clip from chip
# - Pull straight up, don't twist
# - Store clip safely for future use

# Disconnect CH341A programmer from USB

# Reconnect motherboard power
# - Plug in PSU
# - Don't turn on yet
```

### Step 2: First Boot Attempt

**What to Expect:**
- ✅ System may take 30-60 seconds on first boot (normal)
- ✅ BIOS may reset to defaults (expected)
- ✅ Date/time will be wrong (expected)
- ⚠️ May see "Checksum error" or similar (often harmless)
- ⚠️ Fans may run at 100% initially (will normalize)

**Boot Sequence:**
1. Press power button
2. Listen for POST beep (single beep = good)
3. Watch for video output
4. Enter BIOS setup (usually DEL or F2)

**Success Indicators:**
- ✅ System boots
- ✅ BIOS accessible
- ✅ Can load OS
- ✅ All hardware detected

### Step 3: Verify ME Disabled in OS

**Linux:**
```bash
# Install intelmetool
sudo apt install intelmetool

# Check ME status
sudo intelmetool -m

# Expected output:
# ME is disabled
# or
# ME is in manufacturing mode
# or
# ME communication failed (good - means it's neutered)
```

**Alternative Check:**
```bash
# Check for ME modules
lsmod | grep mei

# If no output = ME not loaded (success!)

# Check dmesg
dmesg | grep -i "mei\|me_client"

# Should see errors or "not found" (good!)
```

### Step 4: Stability Testing

**Run for 24-48 hours:**
```bash
# Memory test
sudo apt install memtest86+
# Reboot and select memtest86+ from GRUB
# Let run overnight

# CPU stress test
sudo apt install stress-ng
stress-ng --cpu 0 --timeout 1h --metrics

# Temperature monitoring
sudo apt install lm-sensors
sensors

# Check for throttling or crashes
```

---

## Part 7: Troubleshooting

### System Won't Boot

**Symptom:** No POST, black screen, no beeps

**Recovery:**
```bash
# 1. Re-attach clip to BIOS chip
# 2. Flash original backup

sudo flashrom -p ch341a_spi -w ~/bios_backups/bios_backup_1.bin

# 3. Wait for verification
# 4. Remove clip, try booting again
```

### BIOS Checksum Error

**Symptom:** "CMOS checksum error" on boot

**Fix:**
1. Enter BIOS setup
2. Load defaults (F5 or similar)
3. Save and exit (F10)
4. System should boot normally
5. Reconfigure BIOS settings as needed

### ME Still Showing as Active

**Symptom:** `intelmetool -m` shows ME active

**Possible Causes:**
1. ME_cleaner used `-S` (soft disable) - ME hardware present but neutered
2. Didn't flash cleaned BIOS
3. BIOS updated itself (disable BIOS updates!)

**Verification:**
```bash
# Read current BIOS
sudo flashrom -p ch341a_spi -r ~/current_bios.bin

# Check if it's clean
python3 me_cleaner.py -c ~/current_bios.bin

# Should show ME removed/disabled
```

### Clip Won't Read Chip

**Symptom:** flashrom can't detect chip

**Fixes:**
1. **Check orientation** - Pin 1 alignment critical
2. **Clean contacts** - Isopropyl alcohol on chip pins
3. **Apply pressure** - Hold clip firmly while reading
4. **Check clip** - Bent pins? Replace clip ($5)
5. **Power off** - Motherboard must be fully powered down
6. **Remove CMOS battery** - Discharge all capacitors

### System Unstable After Flash

**Symptom:** Random crashes, freezes, USB issues

**Possible Fixes:**
1. **Update BIOS settings:**
   - Disable "AMT" if present
   - Disable "Intel PTT"
   - Enable "Legacy USB"
2. **Reflash with less aggressive ME_cleaner:**
   ```bash
   # Use only -S flag (soft disable)
   python3 me_cleaner.py -S -O bios_cleaned_safe.bin bios_backup_1.bin
   sudo flashrom -p ch341a_spi -w bios_cleaned_safe.bin
   ```

---

## Part 8: Advanced - Full Coreboot Installation

**For supported motherboards only:**
- ASUS KGPE-D16
- ASUS KCMA-D8
- ThinkPad X200/T400

### Coreboot vs ME_cleaner

| Feature | ME_cleaner | Coreboot |
|---------|-----------|----------|
| **ME Removal** | 95% | 100% (pre-ME boards) |
| **Compatibility** | Most Intel boards | Limited boards |
| **Difficulty** | Easy | Hard |
| **Boot Time** | Same | Faster |
| **Features** | Same | More control |

### Coreboot Installation (Advanced)

```bash
# Install build dependencies
sudo apt install -y git gnat flex bison libncurses5-dev \
    wget zlib1g-dev python nasm sharutils

# Clone Coreboot
git clone https://review.coreboot.org/coreboot
cd coreboot

# Get submodules
git submodule update --init --checkout

# Configure for your board
make menuconfig
# Select your mainboard

# Build
make crossgcc-i386 CPUS=4
make
# This takes 1-2 hours

# Flash
sudo flashrom -p ch341a_spi -w build/coreboot.rom
```

**Coreboot Resources:**
- https://coreboot.org/
- https://www.coreboot.org/Board_Test_Reports
- r/coreboot subreddit

---

## Part 9: Verification and Hardening

### Verify ME Neutralization

```bash
# Install checking tools
sudo apt install -y intelmetool

# Check ME status
sudo intelmetool -m

# Expected output variants:
# 1. "ME is disabled" ✅
# 2. "Communication with ME failed" ✅ (good!)
# 3. "ME is in manufacturing mode" ✅
# 4. "ME is enabled" ❌ (reflash needed)

# Additional checks
sudo dmesg | grep -i mei
# Should show no MEI devices or error loading
```

### Additional Hardening Steps

**1. Disable Remaining Intel Features:**

Enter BIOS and disable:
- ❌ Intel AMT (Active Management Technology)
- ❌ Intel PTT (Platform Trust Technology)
- ❌ Intel Boot Guard (if present)
- ❌ Intel Rapid Start
- ❌ Intel Smart Response

**2. Enable Security Features:**

- ✅ Secure Boot (with your own keys)
- ✅ UEFI password
- ✅ Disable USB boot (after setup)
- ✅ Enable virtualization (VT-x/VT-d for Qubes)

**3. Lock Flash Descriptor:**

```bash
# Prevents runtime BIOS updates
python3 me_cleaner.py -S -d -O bios_locked.bin bios_cleaned.bin
sudo flashrom -p ch341a_spi -w bios_locked.bin
```

---

## Legal and Ethical Notes

### Is This Legal?

**YES** - In most countries:
- ✅ Legal to modify hardware you own
- ✅ Legal to remove surveillance features
- ✅ Legal to use privacy tools
- ✅ Legal to protect from state surveillance

**Legal Precedents:**
- Right to repair laws
- Circumventing access controls on devices you own
- Digital privacy rights

### Is This Ethical?

**Arguments FOR:**
- Protecting privacy is a human right
- ME is an undocumented backdoor
- State surveillance overreach documented (Snowden leaks)
- Open source firmware is more secure

**Arguments AGAINST:**
- ME provides legitimate enterprise features
- Some organizations require ME for management
- May void warranty (usually does)

**Our Position:**
Privacy is not a crime. You have a right to secure your own computer against state-level adversaries. The Five Eyes surveillance apparatus is well-documented, and ME is a known attack vector.

---

## Quick Reference Card

### Emergency Recovery

**System Won't Boot After Flash:**
```bash
# 1. Re-attach clip
# 2. Flash original backup
sudo flashrom -p ch341a_spi -w ~/bios_backups/bios_backup_1.bin
# 3. Boot should work
```

### Verify ME Disabled
```bash
sudo intelmetool -m
# Should NOT show "ME is enabled"
```

### Re-enable ME (If Needed)
```bash
# Flash original backup
sudo flashrom -p ch341a_spi -w ~/bios_backups/bios_backup_1.bin
```

---

## Success Checklist

After completing this guide:

- ✅ Intel ME neutralized (95-100%)
- ✅ System boots normally
- ✅ OS loads without errors
- ✅ `intelmetool` confirms ME disabled
- ✅ System stable for 24+ hours
- ✅ Qubes OS compatible
- ✅ Ready for Eleanor Platform deployment
- ✅ Protected from Five Eyes ME-based surveillance

---

## Additional Resources

**ME_cleaner:**
- GitHub: https://github.com/corna/me_cleaner
- Wiki: https://github.com/corna/me_cleaner/wiki

**Coreboot:**
- Official: https://www.coreboot.org/
- Documentation: https://doc.coreboot.org/

**Community:**
- r/coreboot
- r/privacy
- r/linux
- Level1Techs forums

**ME Research:**
- "Intel ME: The Way of Static Analysis" - Positive Technologies
- "Intel ME Secrets" - Igor Skochinsky
- "Intel ME Manufacturing Mode" - Trammell Hudson

---

**⚠️ FINAL WARNING:**

This procedure can brick your motherboard. Always:
1. Make multiple backups
2. Test thoroughly
3. Have recovery plan
4. Start with less aggressive options
5. Ask for help if stuck

**Privacy is worth the effort. Good luck!** 🔒
