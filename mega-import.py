#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Mega-Batch Import
Load huge batches (10M rows) into temp, then bulk INSERT
Handles duplicates, ultra-fast, simple architecture
"""

import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
MEGA_BATCH_SIZE = 10_000_000  # 10M rows per batch

class Stats:
    def __init__(self):
        self.total_hashed = 0
        self.total_inserted = 0
        self.start = datetime.now()
        self.last_report = self.start
        self.last_count = 0
        self.batches = 0
    
    def update(self, hashed, inserted):
        self.total_hashed += hashed
        self.total_inserted += inserted
        self.batches += 1
        now = datetime.now()
        
        elapsed = (now - self.start).total_seconds()
        avg_speed = self.total_hashed / elapsed if elapsed > 0 else 0
        
        print(f"Batch {self.batches}: {hashed:,} hashed → {inserted:,} new | "
              f"Total: {self.total_inserted:,} | "
              f"Avg: {avg_speed:,.0f}/s")

async def mega_import(filepath: Path, source: str):
    """Import in mega batches with deduplication"""
    
    print("═" * 70)
    print("  DATASEED MASTER-9000: Mega-Batch Import")
    print("  🚀 10M row batches with deduplication")
    print("═" * 70)
    print()
    
    conn = await asyncpg.connect(DB_URL)
    
    before = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Before: {before:,} passwords\n")
    
    await conn.execute("SET synchronous_commit = OFF")
    
    print(f"📂 Processing: {filepath.name}")
    print(f"💾 Batch size: {MEGA_BATCH_SIZE:,} rows")
    print()
    
    stats = Stats()
    start = datetime.now()
    
    batch = []
    batch_num = 0
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            batch.append((password_hash, source))
            
            if len(batch) >= MEGA_BATCH_SIZE:
                # Insert batch
                batch_num += 1
                async with conn.transaction():
                    # Create temp table in transaction
                    await conn.execute("""
                        CREATE TEMP TABLE temp_batch (
                            hash TEXT,
                            source TEXT
                        ) ON COMMIT DROP
                    """)
                    
                    # Copy batch into temp
                    await conn.copy_records_to_table(
                        'temp_batch',
                        records=batch,
                        columns=['hash', 'source']
                    )
                    
                    # Get count before
                    before_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                    
                    # Insert with ON CONFLICT
                    await conn.execute("""
                        INSERT INTO breached_hashes (hash, source)
                        SELECT DISTINCT hash, source FROM temp_batch
                        ON CONFLICT (hash) DO NOTHING
                    """)
                    
                    # Get count after
                    after_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
                    inserted = after_batch - before_batch
                
                stats.update(len(batch), inserted)
                batch = []
    
    # Process remaining
    if batch:
        batch_num += 1
        async with conn.transaction():
            await conn.execute("""
                CREATE TEMP TABLE temp_batch (
                    hash TEXT,
                    source TEXT
                ) ON COMMIT DROP
            """)
            
            await conn.copy_records_to_table(
                'temp_batch',
                records=batch,
                columns=['hash', 'source']
            )
            
            before_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
            
            await conn.execute("""
                INSERT INTO breached_hashes (hash, source)
                SELECT DISTINCT hash, source FROM temp_batch
                ON CONFLICT (hash) DO NOTHING
            """)
            
            after_batch = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
            inserted = after_batch - before_batch
        
        stats.update(len(batch), inserted)
    
    after = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print()
    print("═" * 70)
    print("  🏆 MEGA-BATCH COMPLETE")
    print("═" * 70)
    print(f"✅ Processed: {stats.total_hashed:,} passwords")
    print(f"✅ Inserted: {stats.total_inserted:,} new rows")
    print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if elapsed > 0:
        print(f"⚡ Speed: {stats.total_hashed/elapsed:,.0f} hashed/sec")
    print(f"📊 After: {after:,} total passwords")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./mega-import.py <wordlist.txt> [source_name]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    asyncio.run(mega_import(filepath, source))
