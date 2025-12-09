#!/bin/bash
# Import all breach/password wordlists into BreachVault

set -e  # Exit on error

# Function to download rockyou2024 (1.5B passwords)
download_rockyou2024() {
    echo "📥 Downloading RockYou2024.txt (1.5 billion passwords, ~7GB compressed)..."
    echo "   Source: https://github.com/ohmybahgosh/RockYou2024.txt"
    echo ""
    
    DOWNLOAD_DIR="$HOME/Downloads"
    mkdir -p "$DOWNLOAD_DIR"
    
    cd "$DOWNLOAD_DIR"
    
    if [ -f "rockyou2024.txt" ]; then
        echo "✓ rockyou2024.txt already exists"
        return 0
    fi
    
    echo "   This will download ~7GB and extract to ~26GB"
    read -p "   Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    
    # Download from GitHub release
    echo "   Downloading..."
    wget -O rockyou2024.txt.tar.gz \
        "https://github.com/ohmybahgosh/RockYou2024.txt/releases/download/v1.0/rockyou2024.txt.tar.gz" \
        || curl -L -o rockyou2024.txt.tar.gz \
        "https://github.com/ohmybahgosh/RockYou2024.txt/releases/download/v1.0/rockyou2024.txt.tar.gz"
    
    echo "   Extracting..."
    tar -xzf rockyou2024.txt.tar.gz
    
    echo "   Cleaning up archive..."
    rm rockyou2024.txt.tar.gz
    
    echo "✅ Downloaded to $DOWNLOAD_DIR/rockyou2024.txt"
    return 0
}

# Check if user wants to download rockyou2024
if [ "$1" == "--download-2024" ] || [ "$1" == "-d" ]; then
    download_rockyou2024
    echo ""
    echo "Now run ./import-all.sh to import it"
    exit 0
fi

echo "🔍 Finding all wordlist files..."
echo ""

# Find all potential wordlist files (including rockyou2024)
FOUND_FILES=($(find ~ -type f \( -name "rockyou*.txt" -o -name "*2024*.txt" -o -name "*breach*.txt" -o -name "*passwords*.txt" -o -name "*.wordlist" \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/.cache/*" ! -path "*/.config/*" 2>/dev/null))

# Deduplicate by content hash
declare -A seen_hashes
declare -a FILES

echo "🔎 Checking for duplicates (this may take a moment)..."
for file in "${FOUND_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Get first 1MB hash to quickly identify duplicates
        file_hash=$(head -c 1048576 "$file" | sha256sum | cut -d' ' -f1)
        
        if [ -z "${seen_hashes[$file_hash]}" ]; then
            seen_hashes[$file_hash]="$file"
            FILES+=("$file")
        else
            echo "  ⏭️  Duplicate of ${seen_hashes[$file_hash]}: $file"
        fi
    fi
done
echo ""

if [ ${#FILES[@]} -eq 0 ]; then
    echo "❌ No wordlist files found!"
    echo ""
    echo "Add files manually to import:"
    echo "  FILES=(\"/path/to/wordlist1.txt\" \"/path/to/wordlist2.txt\")"
    exit 1
fi

echo "📋 Unique files to import:"
for file in "${FILES[@]}"; do
    size=$(du -h "$file" | cut -f1)
    lines=$(wc -l < "$file" 2>/dev/null || echo "?")
    echo "  ✓ $file ($size, $lines lines)"
done
echo ""

read -p "Continue with import? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Import each file
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⏭️  Skipping $file (not found)"
        continue
    fi
    
    filename=$(basename "$file")
    echo ""
    echo "📤 Importing $filename..."
    echo "   File: $file"
    
    # Copy file into backend container
    sudo docker cp "$file" breachvault-backend:/tmp/wordlist.txt
    
    # Run import script inside container
    sudo docker compose exec -T backend python << EOF
import asyncio
import hashlib
from app.services.db import db_service

async def import_file():
    print("🔗 Connecting to database...")
    await db_service.connect()
    
    print("📖 Reading file...")
    batch = []
    total = 0
    duplicates = 0
    
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
                
                if total % 100000 == 0:
                    print(f"   Processed: {total:,} passwords...")
        
        # Insert remaining
        if batch:
            async with db_service.pool.acquire() as conn:
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES (\$1, \$2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
    
    print(f"✅ Imported {total:,} passwords from $filename")
    
    # Show total count
    async with db_service.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        print(f"📊 Total passwords in database: {count:,}")
    
    await db_service.disconnect()

asyncio.run(import_file())
EOF
    
    # Clean up
    sudo docker compose exec -T backend rm /tmp/wordlist.txt
    
    echo "✅ Done with $filename"
done

echo ""
echo "🎉 All imports complete!"
echo ""
echo "💡 Tips:"
echo "  • Download RockYou2024 (1.5B passwords): ./import-all.sh --download-2024"
echo "  • Check database count: sudo docker compose exec backend python -c 'import asyncio; from app.services.db import db_service; async def count(): await db_service.connect(); c = await db_service.pool.fetchval(\"SELECT COUNT(*) FROM breached_hashes\"); print(f\"Total: {c:,}\"); await db_service.disconnect(); asyncio.run(count())'"
