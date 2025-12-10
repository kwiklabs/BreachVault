# BreachVault Import on i9 Laptop - Setup Guide

## Prerequisites
Your i9-13980HX will DEMOLISH this workload. Expected: **500K-800K/sec** (vs 100K on i7)

## 1. Setup on i9 Laptop

```bash
# Clone repo
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault

# Install dependencies
sudo apt update
sudo apt install -y docker.io docker-compose python3-psycopg2 parallel

# Start containers
sudo docker compose up -d

# Wait for postgres to be ready
sleep 5

# Install Python deps
pip3 install --user pybloom-live
```

## 2. Copy wordlist files (3 options)

### Option A: USB Drive (fastest for 38GB)
```bash
# On desktop: copy to USB
cp ~/Downloads/weakpass_4.txt /media/usb/

# On laptop: copy from USB
cp /media/usb/weakpass_4.txt ~/Downloads/
```

### Option B: Network transfer (if on same network)
```bash
# On desktop (this server):
# Find IP: ip addr show | grep inet

# On laptop:
rsync -avP --partial mmi@<DESKTOP_IP>:~/Downloads/weakpass_4.txt ~/Downloads/
```

### Option C: Download fresh
```bash
# Download from source on laptop
```

## 3. Split into chunks

```bash
cd ~/BreachVault
./split-wordlist.sh
# Creates 2192 chunks of 1M lines in ~/Downloads/weakpass_chunks/
```

## 4. Build bloom filter from existing data

```bash
# Export current DB to bloom filter (205MB file)
python3 build-bloom-filter.py
# Creates /tmp/breach_bloom_filter.pkl
```

## 5. Run import

```bash
# Simple sequential (RECOMMENDED - no connection issues)
python3 simple-sequential.py

# OR parallel (20 workers on i9)
# Edit parallel-chunks.sh: WORKERS=20
./parallel-chunks.sh
```

## Expected Performance on i9

- **CPU**: 24 cores @ 5.6GHz boost
- **RAM**: 32GB DDR5 (80GB/s bandwidth)
- **Speed**: 500-800K passwords/sec
- **Time**: ~1-2 hours for 2.2B passwords

## Monitor Progress

```bash
# Watch DB growth live
./watch-db.sh

# Count remaining chunks
ls ~/Downloads/weakpass_chunks/ | wc -l
```

## Troubleshooting

**"too many clients"**: Reduce WORKERS in parallel-chunks.sh
**Slow performance**: Use simple-sequential.py instead of parallel
**Out of memory**: Reduce batch size in scripts

---

Your i9 is a BEAST - it'll process this 2-3x faster than the desktop!
