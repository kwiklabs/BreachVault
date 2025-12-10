#!/bin/bash
# DATASEED MASTER-9000: Ultimate Import Pipeline
# Hash in Python, pipe to psql COPY - THE FASTEST WAY

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HASH_SCRIPT="$SCRIPT_DIR/hash-to-stdout.py"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <wordlist.txt> <source_name>"
    echo ""
    echo "Example:"
    echo "  $0 ~/Downloads/weakpass_4.txt weakpass_4"
    exit 1
fi

WORDLIST="$1"
SOURCE="$2"

echo "═══════════════════════════════════════════════════════════"
echo "  DATASEED MASTER-9000: Ultimate COPY Pipeline"
echo "  🚀 Python Hash → psql COPY = Maximum Performance"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Make hash script executable
chmod +x "$HASH_SCRIPT"

# Get before count
BEFORE=$(sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes" | tr -d ' ')
echo "📊 Database before: $BEFORE passwords"
echo ""

echo "📂 Processing: $(basename "$WORDLIST")"
echo "🔧 Strategy: Python streaming SHA-256 → psql COPY FROM STDIN"
echo ""

START=$(date +%s)

# THE PIPELINE: hash-to-stdout | docker exec psql COPY
"$HASH_SCRIPT" "$WORDLIST" "$SOURCE" | \
    sudo docker exec -i breachvault-postgres psql \
    -U breachvault \
    -d breachvault \
    -c "SET synchronous_commit = OFF; COPY breached_hashes (hash, source) FROM STDIN WITH (FORMAT TEXT, DELIMITER E'\t')" \
    2>&1 | grep -v "^COPY"

END=$(date +%s)
ELAPSED=$((END - START))

# Get after count
AFTER=$(sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes" | tr -d ' ')
NEW=$((AFTER - BEFORE))

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🏆 ULTIMATE PIPELINE COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo "✅ New rows: $NEW"
echo "⏱️  Time: ${ELAPSED}s ($((ELAPSED / 60)) min)"
if [[ $ELAPSED -gt 0 ]]; then
    SPEED=$((AFTER - BEFORE))
    SPEED=$((SPEED / ELAPSED))
    echo "⚡ Speed: ${SPEED} rows/sec"
fi
echo "📊 Database after: $AFTER total passwords"
