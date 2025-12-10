#!/bin/bash
# Migrate to i9 laptop for 2-3x performance

LAPTOP_IP="YOUR_LAPTOP_IP"  # Replace with your i9 laptop IP
LAPTOP_USER="YOUR_USERNAME"  # Replace with your username

echo "═══════════════════════════════════════════════════════════"
echo "  Migrating to i9-13980HX for Maximum Performance"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. Transfer bloom filter (205MB - fast)
echo "1. Transferring bloom filter..."
rsync -avz --progress /tmp/breach_bloom_filter.pkl $LAPTOP_USER@$LAPTOP_IP:/tmp/

# 2. Transfer remaining chunks
echo ""
echo "2. Transferring remaining chunks..."
rsync -avz --progress ~/Downloads/weakpass_chunks/ $LAPTOP_USER@$LAPTOP_IP:~/Downloads/weakpass_chunks/

# 3. Transfer scripts
echo ""
echo "3. Transferring scripts..."
rsync -avz --progress ~/kwiklabs/BreachVault/*.py $LAPTOP_USER@$LAPTOP_IP:~/BreachVault/

echo ""
echo "✅ Transfer complete!"
echo ""
echo "On your i9 laptop, run:"
echo "  cd ~/BreachVault"
echo "  python3 simple-sequential.py"
echo ""
echo "Expected: 400K-600K/sec (2-3x faster than i7)"

