#!/bin/bash
# Efficient streaming import for massive wordlists
# Streams data directly without copying entire files

set -e

WORDLIST="$1"

if [ -z "$WORDLIST" ]; then
    echo "Usage: $0 <wordlist.txt>"
    exit 1
fi

if [ ! -f "$WORDLIST" ]; then
    echo "Error: File not found: $WORDLIST"
    exit 1
fi

FILENAME=$(basename "$WORDLIST")

echo "🚀 Streaming import: $FILENAME"
echo "📊 Processing in batches of 10K..."
echo ""

# Stream file line by line, hash on the fly, batch insert
cat "$WORDLIST" | sudo docker compose exec -T backend python << 'EOF'
import sys
import asyncio
import hashlib
from app.services.db import db_service
import time

async def stream_import():
    start_time = time.time()
    await db_service.connect()
    
    batch = []
    total = 0
    BATCH_SIZE = 10000
    
    print(f"🔗 Connected to database")
    print(f"📖 Streaming and hashing...")
    
    for line in sys.stdin:
        password = line.strip()
        if not password:
            continue
        
        # Hash password
        hash_obj = hashlib.sha256(password.encode("utf-8", errors="ignore"))
        password_hash = hash_obj.hexdigest()
        
        batch.append((password_hash, sys.argv[1] if len(sys.argv) > 1 else "stream"))
        total += 1
        
        # Insert batch
        if len(batch) >= BATCH_SIZE:
            async with db_service.pool.acquire() as conn:
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
            batch = []
            
            # Progress update
            if total % 100000 == 0:
                elapsed = time.time() - start_time
                rate = total / elapsed if elapsed > 0 else 0
                print(f"   ⚡ {total:,} passwords | {rate:,.0f}/sec | {elapsed:.1f}s")
    
    # Insert remaining
    if batch:
        async with db_service.pool.acquire() as conn:
            await conn.executemany(
                "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                batch
            )
    
    elapsed = time.time() - start_time
    rate = total / elapsed if elapsed > 0 else 0
    print(f"\n✅ Imported {total:,} passwords in {elapsed:.1f}s ({rate:,.0f}/sec)")
    
    # Show total
    count = await db_service.pool.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Total in database: {count:,} passwords")
    
    await db_service.disconnect()

asyncio.run(stream_import())
EOF
