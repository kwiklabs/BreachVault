#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Simple Batch Import
Clean, simple, with real-time feedback
"""

import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime
from time import time

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
BATCH_SIZE = 50_000

async def simple_import(filepath: Path, source: str):
    print("╔" + "═" * 68 + "╗")
    print("║" + " DATASEED MASTER-9000: Simple Batch Import".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Connect
    print("🔌 Connecting to database...")
    try:
        conn = await asyncpg.connect(DB_URL)
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Get starting count
    before = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Current database: {before:,} passwords")
    print()
    
    # Optimize
    await conn.execute("SET synchronous_commit = OFF")
    
    # File info
    file_size = filepath.stat().st_size
    print(f"📂 File: {filepath.name}")
    print(f"💾 Size: {file_size / (1024**3):.2f} GB")
    print(f"⚙️  Batch size: {BATCH_SIZE:,} rows")
    print()
    print("─" * 70)
    print()
    
    total = 0
    inserted = 0
    batch = []
    batch_num = 0
    start_time = time()
    
    print("🚀 Starting import...\n")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            # Hash it
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            batch.append((password_hash, source))
            total += 1
            
            # When batch full, insert
            if len(batch) >= BATCH_SIZE:
                batch_num += 1
                before_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                
                # Insert batch
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
                
                after_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                new = after_batch - before_batch
                inserted += new
                
                # Stats
                elapsed = time() - start_time
                speed = total / elapsed if elapsed > 0 else 0
                
                # Progress bar
                print(f"Batch #{batch_num:>6} | "
                      f"Processed: {total:>12,} | "
                      f"New: {inserted:>12,} | "
                      f"Speed: {speed:>8,.0f}/s | "
                      f"Time: {elapsed:>6.1f}s")
                
                batch = []
    
    # Last batch
    if batch:
        batch_num += 1
        before_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        
        await conn.executemany(
            "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
            batch
        )
        
        after_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        new = after_batch - before_batch
        inserted += new
        
        elapsed = time() - start_time
        speed = total / elapsed if elapsed > 0 else 0
        
        print(f"Batch #{batch_num:>6} | "
              f"Processed: {total:>12,} | "
              f"New: {inserted:>12,} | "
              f"Speed: {speed:>8,.0f}/s | "
              f"Time: {elapsed:>6.1f}s")
    
    # Final count
    after = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    
    elapsed = time() - start_time
    
    print()
    print("─" * 70)
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " ✅ IMPORT COMPLETE".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print(f"  📥 Processed:   {total:,} passwords")
    print(f"  ✨ Inserted:    {inserted:,} new rows")
    print(f"  ⏱️  Time:        {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if elapsed > 0:
        print(f"  ⚡ Avg Speed:   {total/elapsed:,.0f} passwords/sec")
    print(f"  📊 Total Now:   {after:,} passwords")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./simple-import.py <wordlist> [source_name]")
        print()
        print("Example:")
        print("  ./simple-import.py ~/Downloads/rockyou.txt rockyou")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    asyncio.run(simple_import(filepath, source))
