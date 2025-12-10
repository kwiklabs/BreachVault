#!/usr/bin/env python3
"""
DATASEED MASTER-9000: True Streaming Import
Batches of 100K rows - memory efficient, fast, handles duplicates
"""

import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
BATCH_SIZE = 100_000  # Sweet spot: memory vs speed

class Stats:
    def __init__(self):
        self.total = 0
        self.inserted = 0
        self.start = datetime.now()
        self.last_report = self.start
        self.last_count = 0
    
    def report(self, batch_size, new_rows):
        self.total += batch_size
        self.inserted += new_rows
        now = datetime.now()
        
        if (now - self.last_report).total_seconds() >= 3:
            elapsed = (now - self.start).total_seconds()
            current = (self.total - self.last_count) / (now - self.last_report).total_seconds()
            avg = self.total / elapsed if elapsed > 0 else 0
            
            print(f"\r✨ {self.total:,} processed | {self.inserted:,} new | "
                  f"⚡ {current:,.0f}/s | 📊 {avg:,.0f}/s avg", 
                  end='', flush=True)
            
            self.last_report = now
            self.last_count = self.total

async def streaming_import(filepath: Path, source: str):
    print("═" * 70)
    print("  DATASEED MASTER-9000: Streaming Import")
    print("  🚀 100K batches - Memory efficient + Deduplication")
    print("═" * 70)
    print()
    
    conn = await asyncpg.connect(DB_URL)
    
    before = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Before: {before:,} passwords\n")
    
    await conn.execute("SET synchronous_commit = OFF")
    
    print(f"📂 Processing: {filepath.name}")
    print(f"💾 Batch size: {BATCH_SIZE:,}")
    print()
    
    stats = Stats()
    start = datetime.now()
    batch = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            batch.append((password_hash, source))
            
            if len(batch) >= BATCH_SIZE:
                # Process batch in transaction
                before_insert = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                    batch
                )
                
                after_insert = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                new_rows = after_insert - before_insert
                
                stats.report(len(batch), new_rows)
                batch = []
    
    # Last batch
    if batch:
        before_insert = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        
        await conn.executemany(
            "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
            batch
        )
        
        after_insert = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
        new_rows = after_insert - before_insert
        stats.report(len(batch), new_rows)
    
    after = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print("\n")
    print("═" * 70)
    print("  🏆 STREAMING COMPLETE")
    print("═" * 70)
    print(f"✅ Processed: {stats.total:,} passwords")
    print(f"✅ Inserted: {stats.inserted:,} new rows")
    print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min, {elapsed/3600:.2f} hrs)")
    if elapsed > 0:
        print(f"⚡ Speed: {stats.total/elapsed:,.0f}/s")
    print(f"📊 After: {after:,} total")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./streaming-import.py <wordlist> [source]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    asyncio.run(streaming_import(filepath, source))
