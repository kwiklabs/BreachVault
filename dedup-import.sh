#!/bin/bash
# DATASEED MASTER-9000: Ultimate Import with Deduplication
# Strategy: COPY to temp table → INSERT with ON CONFLICT

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HASH_SCRIPT="$SCRIPT_DIR/hash-to-stdout.py"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <wordlist.txt> <source_name>"
    exit 1
fi

WORDLIST="$1"
SOURCE="$2"
TEMP_TABLE="temp_import_$$"

echo "═══════════════════════════════════════════════════════════"
echo "  DATASEED MASTER-9000: Dedup Import Pipeline"
echo "  🚀 COPY temp → INSERT with ON CONFLICT = Fast + Safe"
echo "═══════════════════════════════════════════════════════════"
echo ""

chmod +x "$HASH_SCRIPT"

BEFORE=$(sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes" | tr -d ' ')
echo "📊 Database before: $BEFORE passwords"
echo ""

echo "📂 Processing: $(basename "$WORDLIST")"
echo "🔧 Strategy: COPY → temp → INSERT with ON CONFLICT"
echo ""

START=$(date +%s)

# Create temp table
sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -c "
    CREATE TEMP TABLE $TEMP_TABLE (
        hash TEXT,
        source TEXT
    );
" > /dev/null

# Hash and COPY into temp table
echo "⚡ Hashing and loading into temp table..."
"$HASH_SCRIPT" "$WORDLIST" "$SOURCE" | \
    sudo docker exec -i breachvault-postgres psql \
    -U breachvault \
    -d breachvault \
    -c "COPY $TEMP_TABLE (hash, source) FROM STDIN WITH (FORMAT TEXT, DELIMITER E'\t')" \
    2>&1 | grep -v "^COPY"

# INSERT from temp to main with ON CONFLICT
echo ""
echo "💾 Inserting with deduplication..."
sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -c "
    SET synchronous_commit = OFF;
    
    INSERT INTO breached_hashes (hash, source)
    SELECT DISTINCT hash, source FROM $TEMP_TABLE
    ON CONFLICT (hash) DO NOTHING;
    
    DROP TABLE $TEMP_TABLE;
" > /dev/null

END=$(date +%s)
ELAPSED=$((END - START))

AFTER=$(sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes" | tr -d ' ')
NEW=$((AFTER - BEFORE))

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🏆 DEDUP PIPELINE COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo "✅ New rows: $NEW"
echo "⏱️  Time: ${ELAPSED}s ($((ELAPSED / 60)) min)"
if [[ $ELAPSED -gt 0 && $NEW -gt 0 ]]; then
    SPEED=$((NEW / ELAPSED))
    echo "⚡ Speed: ${SPEED} new rows/sec"
fi
echo "📊 Database after: $AFTER total passwords"
