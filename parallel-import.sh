#!/bin/bash
# Ultra-optimized parallel password import for BreachVault
# Uses GNU parallel + multiple Python workers for maximum throughput

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
WORKERS=${WORKERS:-4}  # Number of parallel workers
BATCH_SIZE=${BATCH_SIZE:-50000}  # Hashes per batch (larger = faster)
CHUNK_LINES=${CHUNK_LINES:-100000}  # Lines per chunk for splitting

echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo -e "${PURPLE}    BreachVault Parallel Import Engine     ${NC}"
echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo ""

# Check for GNU parallel
if ! command -v parallel &> /dev/null; then
    echo -e "${YELLOW}⚠️  GNU parallel not found. Installing...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt install -y parallel
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y parallel
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm parallel
    else
        echo -e "${RED}❌ Cannot install GNU parallel automatically${NC}"
        echo "Please install manually: apt/dnf/pacman install parallel"
        exit 1
    fi
fi

# Scan for wordlists
echo -e "${CYAN}🔍 Scanning for wordlists...${NC}"

declare -a WORDLISTS=()
declare -A FILE_INFO

scan_directory() {
    local dir="$1"
    
    # Skip trash/temp directories
    if [[ "$dir" == *"Trash"* ]] || [[ "$dir" == *"trash"* ]] || \
       [[ "$dir" == *".cache"* ]] || [[ "$dir" == *"tmp"* ]]; then
        return
    fi
    
    # Search for common password list patterns
    while IFS= read -r file; do
        # Calculate file hash for deduplication (first 1MB)
        local hash=$(head -c 1048576 "$file" 2>/dev/null | sha256sum | cut -d' ' -f1)
        
        # Skip if we've seen this file before
        if [[ -n "${FILE_INFO[$hash]}" ]]; then
            continue
        fi
        
        local size=$(du -sh "$file" | cut -f1)
        local lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        
        FILE_INFO[$hash]="$file|$size|$lines"
        WORDLISTS+=("$file")
    done < <(find "$dir" -maxdepth 3 -type f \( \
        -iname "rockyou*.txt" -o \
        -iname "crackstation*.txt" -o \
        -iname "weakpass*.txt" -o \
        -iname "breach*.txt" -o \
        -iname "passwords*.txt" \
    \) 2>/dev/null)
}

# Get git repository root
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Scan common locations
scan_directory "$HOME/Downloads"
scan_directory "$HOME/wordlists"
scan_directory "$GIT_ROOT"
scan_directory .

if [ ${#WORDLISTS[@]} -eq 0 ]; then
    echo -e "${RED}❌ No wordlists found${NC}"
    echo "Searched: \$HOME/Downloads, \$HOME/wordlists, git root, current directory"
    exit 1
fi

# Display found files
echo ""
echo -e "${GREEN}Found ${#WORDLISTS[@]} wordlist(s):${NC}"
echo ""

TOTAL_PASSWORDS=0

for file in "${WORDLISTS[@]}"; do
    for hash in "${!FILE_INFO[@]}"; do
        info="${FILE_INFO[$hash]}"
        filepath="${info%%|*}"
        
        if [ "$filepath" = "$file" ]; then
            size=$(echo "$info" | cut -d'|' -f2)
            lines=$(echo "$info" | cut -d'|' -f3)
            
            TOTAL_PASSWORDS=$((TOTAL_PASSWORDS + lines))
            
            echo -e "  ${GREEN}✓${NC} $(basename "$file")"
            echo -e "     ├─ Size: ${size}"
            echo -e "     ├─ Lines: $(printf "%'d" $lines)"
            echo -e "     └─ Path: $file"
        fi
    done
done

echo ""
echo -e "${CYAN}Total: $(printf "%'d" $TOTAL_PASSWORDS) passwords across ${#WORDLISTS[@]} file(s)${NC}"
echo ""
echo -e "${YELLOW}⚙️  Workers: ${WORKERS}${NC}"
echo -e "${YELLOW}⚙️  Batch size: $(printf "%'d" $BATCH_SIZE) hashes/batch${NC}"
echo ""
echo -e "${YELLOW}⚠️  Ready to import into BreachVault database${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo -e "${PURPLE}          Starting Import Process          ${NC}"
echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo ""

# Process each file
FILE_COUNT=0

for file in "${WORDLISTS[@]}"; do
    FILE_COUNT=$((FILE_COUNT + 1))
    FILENAME=$(basename "$file")
    
    echo -e "${BLUE}[${FILE_COUNT}/${#WORDLISTS[@]}] 📤 Importing $FILENAME${NC}"
    echo -e "   Path: $file"
    echo ""
    
    # Create Python worker script
    cat > /tmp/worker_import.py << 'WORKER_SCRIPT'
import sys
import asyncio
import hashlib
import asyncpg
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://breachvault:breachpass@localhost:5433/breachvault")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50000"))

async def worker_import():
    """Process stdin lines in parallel batches"""
    conn = await asyncpg.connect(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
    
    try:
        batch = []
        total = 0
        start_time = datetime.now()
        
        for line in sys.stdin:
            password = line.strip()
            if not password:
                continue
            
            # Hash password
            password_hash = hashlib.sha256(password.encode("utf-8", errors="ignore")).hexdigest()
            source = sys.argv[1] if len(sys.argv) > 1 else "import"
            
            batch.append((password_hash, source))
            total += 1
            
            # Batch insert
            if len(batch) >= BATCH_SIZE:
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
                batch = []
                
                # Progress (every 100K)
                if total % 100000 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = total / elapsed if elapsed > 0 else 0
                    print(f"   ⚡ {total:,} passwords | {rate:,.0f}/sec", file=sys.stderr, flush=True)
        
        # Insert remaining
        if batch:
            await conn.executemany(
                "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                batch
            )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = total / elapsed if elapsed > 0 else 0
        print(f"   Worker processed {total:,} in {elapsed:.1f}s ({rate:,.0f}/sec)", file=sys.stderr, flush=True)
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(worker_import())
WORKER_SCRIPT
    
    # Export environment variables for workers
    export DATABASE_URL="postgresql://breachvault:breachpass@localhost:5433/breachvault"
    export BATCH_SIZE="$BATCH_SIZE"
    
    # Use GNU parallel to split work across workers
    # --pipe: feed stdin to workers in chunks
    # --block: size of each chunk (in bytes, -1 = auto)
    # -j: number of parallel workers
    # --round-robin: distribute lines evenly
    
    echo -e "   ${CYAN}🚀 Processing with ${WORKERS} parallel workers...${NC}"
    
    START_TIME=$(date +%s)
    
    cat "$file" | parallel \
        --pipe \
        --round-robin \
        -j "$WORKERS" \
        --block -1 \
        "python3 /tmp/worker_import.py '$FILENAME'"
    
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    
    # Get final database count
    DB_COUNT=$(sudo docker compose exec -T postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes;" 2>/dev/null | xargs || echo "0")
    
    echo ""
    echo -e "${GREEN}✅ Done with $FILENAME${NC}"
    echo -e "   Total time: ${ELAPSED}s"
    echo -e "   Database total: $(printf "%'d" $DB_COUNT) passwords"
    echo -e "${BLUE}────────────────────────────────────────────${NC}"
    echo ""
done

# Cleanup
rm -f /tmp/worker_import.py

echo ""
echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All imports complete!${NC}"
echo ""

# Final stats
FINAL_COUNT=$(sudo docker compose exec -T postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes;" 2>/dev/null | xargs || echo "0")
echo -e "${CYAN}📊 Final database count: $(printf "%'d" $FINAL_COUNT) passwords${NC}"
echo ""
