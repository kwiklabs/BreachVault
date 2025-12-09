#!/bin/bash
# Import all breach/password wordlists into BreachVault

set -e  # Exit on error

# Colors for better visual feedback
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Emoji alternatives for systems without emoji support
EMOJI_SEARCH="🔍"
EMOJI_CHECK="✓"
EMOJI_SKIP="⏭️"
EMOJI_DOWNLOAD="📥"
EMOJI_UPLOAD="📤"
EMOJI_SUCCESS="✅"
EMOJI_ERROR="❌"
EMOJI_INFO="💡"
EMOJI_ROCKET="🚀"
EMOJI_DATABASE="📊"
EMOJI_BOOK="📖"
EMOJI_LINK="🔗"
EMOJI_PARTY="🎉"

# Function to download rockyou2024 (1.5B passwords)
download_rockyou2024() {
    echo -e "${CYAN}${EMOJI_DOWNLOAD} Downloading RockYou2024.txt${NC}"
    echo -e "${BOLD}   • 1.5 billion passwords${NC}"
    echo -e "${BOLD}   • ~26GB uncompressed${NC}"
    echo -e "   ${BLUE}Source: Magnet link via torrent${NC}"
    echo ""
    
    DOWNLOAD_DIR="$HOME/Downloads"
    mkdir -p "$DOWNLOAD_DIR"
    
    cd "$DOWNLOAD_DIR"
    
    if [ -f "rockyou2024.txt" ]; then
        echo -e "${GREEN}${EMOJI_CHECK} rockyou2024.txt already exists${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  RockYou2024 must be downloaded via torrent or direct link${NC}"
    echo ""
    echo -e "${CYAN}Option 1 - Torrent (fastest):${NC}"
    echo -e "  Magnet: ${BOLD}magnet:?xt=urn:btih:2eba19c1e8c83aa3f6e47360e1a5c1f43b73a852&dn=rockyou2024.txt${NC}"
    echo ""
    echo -e "${CYAN}Option 2 - Direct download:${NC}"
    echo -e "  wget https://weakpass.com/wordlist/2024 -O rockyou2024.txt.gz"
    echo -e "  gunzip rockyou2024.txt.gz"
    echo ""
    echo -e "${CYAN}Option 3 - Kaggle:${NC}"
    echo -e "  https://www.kaggle.com/datasets/wjburns/common-password-list-rockyou2024txt"
    echo ""
    echo -e "${YELLOW}After downloading, place the file in:${NC}"
    echo -e "  ${BOLD}$DOWNLOAD_DIR/rockyou2024.txt${NC}"
    echo ""
    echo -e "${GREEN}Then run: ${BOLD}./import-all.sh${NC}"
    
    return 1
}

# Check if user wants to download rockyou2024
if [ "$1" == "--download-2024" ] || [ "$1" == "-d" ]; then
    download_rockyou2024
    echo ""
    echo -e "${PURPLE}${EMOJI_ROCKET} Now run ${BOLD}./import-all.sh${NC}${PURPLE} to import it${NC}"
    exit 0
fi

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║     ${EMOJI_ROCKET} BreachVault Wordlist Importer     ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}${EMOJI_SEARCH} Finding all wordlist files...${NC}"

# Find all potential wordlist files (including rockyou2024)
FOUND_FILES=($(find ~ -type f \( -name "rockyou*.txt" -o -name "RockYou*.txt" -o -name "breach*.txt" -o -name "Breach*.txt" \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/.cache/*" ! -path "*/.config/*" ! -path "*/Trash/*" ! -path "*/.Trash*/*" ! -path "*/trash/*" 2>/dev/null))

# Deduplicate by content hash
declare -A seen_hashes
declare -a FILES

echo -e "${CYAN}🔎 Checking for duplicates...${NC}"
duplicates_found=0
for file in "${FOUND_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Get first 1MB hash to quickly identify duplicates
        file_hash=$(head -c 1048576 "$file" | sha256sum | cut -d' ' -f1)
        
        if [ -z "${seen_hashes[$file_hash]}" ]; then
            seen_hashes[$file_hash]="$file"
            FILES+=("$file")
        else
            echo -e "  ${YELLOW}${EMOJI_SKIP} ${NC}${file}"
            echo -e "     ${CYAN}↳ Duplicate of ${seen_hashes[$file_hash]}${NC}"
            duplicates_found=$((duplicates_found + 1))
        fi
    fi
done

if [ $duplicates_found -gt 0 ]; then
    echo -e "${GREEN}${EMOJI_CHECK} Filtered out $duplicates_found duplicate(s)${NC}"
fi
echo ""

if [ ${#FILES[@]} -eq 0 ]; then
    echo -e "${RED}${EMOJI_ERROR} No wordlist files found!${NC}"
    echo ""
    echo -e "${YELLOW}${EMOJI_INFO} Tip: Download RockYou2024 with:${NC}"
    echo -e "   ${BOLD}./import-all.sh --download-2024${NC}"
    exit 1
fi

echo -e "${BOLD}${GREEN}📋 Unique files to import:${NC}"
total_lines=0
for file in "${FILES[@]}"; do
    size=$(du -h "$file" | cut -f1)
    lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    total_lines=$((total_lines + lines))
    echo -e "  ${GREEN}${EMOJI_CHECK}${NC} ${BOLD}$(basename "$file")${NC}"
    echo -e "     ${CYAN}├─ Size: $size${NC}"
    echo -e "     ${CYAN}├─ Lines: $(printf "%'d" $lines)${NC}"
    echo -e "     ${CYAN}└─ Path: $file${NC}"
done
echo ""
echo -e "${BOLD}${PURPLE}Total: $(printf "%'d" $total_lines) passwords across ${#FILES[@]} file(s)${NC}"
echo ""

echo -e "${YELLOW}⚠️  Ready to import into BreachVault database${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}${CYAN}════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}          Starting Import Process          ${NC}"
echo -e "${BOLD}${CYAN}════════════════════════════════════════════${NC}"
echo ""

# Import each file
file_count=0
for file in "${FILES[@]}"; do
    file_count=$((file_count + 1))
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}${EMOJI_SKIP} Skipping $file (not found)${NC}"
        continue
    fi
    
    filename=$(basename "$file")
    echo -e "${BOLD}${PURPLE}[$file_count/${#FILES[@]}] ${EMOJI_UPLOAD} Importing $filename${NC}"
    echo -e "   ${CYAN}Path: $file${NC}"
    
    # Copy file into backend container
    echo -e "   ${CYAN}⬆️  Uploading to container...${NC}"
    sudo docker cp "$file" breachvault-backend:/tmp/wordlist.txt
    
    # Run import script inside container
    echo -e "   ${GREEN}${EMOJI_ROCKET} Processing...${NC}"
    echo ""
    sudo docker compose exec -T backend python << EOF
import asyncio
import hashlib
from app.services.db import db_service

async def import_file():
    import time
    start_time = time.time()
    
    print("\033[0;36m🔗 Connecting to database...\033[0m")
    await db_service.connect()
    
    print("\033[0;36m📖 Reading and hashing passwords...\033[0m")
    batch = []
    total = 0
    duplicates = 0
    last_update = time.time()
    
    with open("/tmp/wordlist.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            # Hash password
            hash_obj = hashlib.sha256(password.encode("utf-8"))
            password_hash = hash_obj.hexdigest()
            
            batch.append((password_hash, "$filename"))
            total += 1
            
            # Insert batch every 10K
            if len(batch) >= 10000:
                async with db_service.pool.acquire() as conn:
                    result = await conn.executemany(
                        "INSERT INTO breached_hashes (hash, source) VALUES (\$1, \$2) ON CONFLICT (hash) DO NOTHING",
                        batch
                    )
                batch = []
                
                # Update progress with speed calculation
                if total % 100000 == 0:
                    elapsed = time.time() - start_time
                    rate = total / elapsed if elapsed > 0 else 0
                    print(f"\033[1;33m   ⚡ {total:,} passwords | {rate:,.0f}/sec | {elapsed:.1f}s elapsed\033[0m")
        
        # Insert remaining
        if batch:
            async with db_service.pool.acquire() as conn:
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES (\$1, \$2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
    
    elapsed = time.time() - start_time
    rate = total / elapsed if elapsed > 0 else 0
    print(f"\033[1;32m✅ Imported {total:,} passwords in {elapsed:.1f}s ({rate:,.0f}/sec)\033[0m")
    
    # Show total count
    async with db_service.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        print(f"\033[1;35m📊 Total in database: {count:,} passwords\033[0m")
    
    await db_service.disconnect()

asyncio.run(import_file())
EOF
    
    # Clean up
    sudo docker compose exec -T backend rm /tmp/wordlist.txt 2>/dev/null
    
    echo ""
    echo -e "${GREEN}${EMOJI_SUCCESS} Done with $filename${NC}"
    echo -e "${CYAN}────────────────────────────────────────────${NC}"
    echo ""
done

echo ""
echo -e "${BOLD}${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║   ${EMOJI_PARTY} All Imports Complete! ${EMOJI_PARTY}           ║${NC}"
echo -e "${BOLD}${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${PURPLE}${EMOJI_INFO} Next steps:${NC}"
echo -e "  ${CYAN}•${NC} Download RockYou2024 (1.5B passwords):"
echo -e "    ${BOLD}./import-all.sh --download-2024${NC}"
echo ""
echo -e "  ${CYAN}•${NC} Test password checker:"
echo -e "    ${BOLD}http://localhost:3000${NC}"
echo ""
echo -e "  ${CYAN}•${NC} Check database stats:"
echo -e "    ${BOLD}sudo docker compose exec backend python -c 'import asyncio; from app.services.db import db_service; async def count(): await db_service.connect(); c = await db_service.pool.fetchval(\"SELECT COUNT(*) FROM breached_hashes\"); print(f\"${EMOJI_DATABASE} Total: {c:,}\"); await db_service.disconnect(); asyncio.run(count())'${NC}"
echo ""
