#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Ultra-Fast COPY with Deduplication
Strategy:
1. Hash passwords in Python (fast)
2. COPY into temp table (ultra-fast, no constraints)
3. INSERT INTO main table with ON CONFLICT DO NOTHING (PostgreSQL handles dedup)

Expected: 300K-500K/sec sustained (2.2B in 60-90 minutes)
"""

import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime
import tempfile

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
BUFFER_SIZE = 1_000_000  # 1M rows per temp table batch

class Stats:
    def __init__(self):
        self.total_hashed = 0
        self.total_inserted = 0
        self.start = datetime.now()
        self.last_report = self.start
        self.last_count = 0
    
    def update(self, hashed, inserted):
        self.total_hashed += hashed
        self.total_inserted += inserted
        now = datetime.now()
        
        # Report every 3 seconds
        if (now - self.last_report).total_seconds() >= 3:
            elapsed = (now - self.start).total_seconds()
            current_speed = (self.total_hashed - self.last_count) / (now - self.last_report).total_seconds()
            avg_speed = self.total_hashed / elapsed if elapsed > 0 else 0
            
            print(f"\r✨ {self.total_hashed:,} hashed → "
                  f"{self.total_inserted:,} inserted | "
                  f"⚡ {current_speed:,.0f}/s | "
                  f"📊 {avg_speed:,.0f}/s avg", end='', flush=True)
            
            self.last_report = now
            self.last_count = self.total_hashed

async def ultra_import(filepath: Path, source: str):
    """Import using temp table COPY + INSERT strategy"""
    
    print("═" * 70)
    print("  DATASEED MASTER-9000: Ultra-Fast Deduplicating Import")
    print("  🚀 COPY to temp → INSERT with ON CONFLICT = Maximum Speed")
    print("═" * 70)
    print()
    
    # Connect
    conn = await asyncpg.connect(DB_URL)
    
    # Get before count
    before = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Database before: {before:,} passwords\n")
    
    # Optimize settings
    await conn.execute("SET synchronous_commit = OFF")
    await conn.execute("SET max_parallel_workers_per_gather = 8")
    
    stats = Stats()
    
    print(f"📂 Processing: {filepath.name}")
    print(f"🔧 Strategy: Python hash → COPY temp → INSERT main")
    print(f"💾 Batch size: {BUFFER_SIZE:,} rows")
    print()
    
    start = datetime.now()
    batch_num = 0
    
    # Process file in batches
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            batch_num += 1
            
            # Create temp file for COPY
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tsv') as tmp:
                tmp_path = tmp.name
                rows_in_batch = 0
                
                # Read and hash chunk
                for line in f:
                    password = line.strip()
                    if not password:
                        continue
                    
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    tmp.write(f"{password_hash}\t{source}\n")
                    rows_in_batch += 1
                    
                    if rows_in_batch >= BUFFER_SIZE:
                        break
                
                if rows_in_batch == 0:
                    break  # EOF
            
            # Create temp table
            temp_table = f"temp_import_{batch_num}"
            await conn.execute(f"""
                CREATE TEMP TABLE {temp_table} (
                    password_hash VARCHAR(64),
                    source VARCHAR(100)
                ) ON COMMIT DROP
            """)
            
            # COPY into temp (blazing fast, no constraints)
            with open(tmp_path, 'r') as tmp_file:
                await conn.copy_to_table(
                    temp_table,
                    source=tmp_file,
                    columns=['password_hash', 'source'],
                    format='text',
                    delimiter='\t'
                )
            
            # INSERT from temp to main with dedup
            inserted = await conn.fetchval(f"""
                INSERT INTO breached_hashes (password_hash, source)
                SELECT DISTINCT password_hash, source FROM {temp_table}
                ON CONFLICT (password_hash) DO NOTHING
                RETURNING (SELECT COUNT(*) FROM breached_hashes)
            """)
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
            stats.update(rows_in_batch, inserted - (before + stats.total_inserted))
            
            if rows_in_batch < BUFFER_SIZE:
                break  # Last batch
    
    # Get after count
    after = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    new_rows = after - before
    
    print("\n")
    print("═" * 70)
    print("  🏆 ULTRA-FAST IMPORT COMPLETE")
    print("═" * 70)
    print(f"✅ Processed: {stats.total_hashed:,} passwords")
    print(f"✅ New rows: {new_rows:,}")
    print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"⚡ Speed: {stats.total_hashed/elapsed:,.0f} passwords/sec")
    print(f"📊 Database after: {after:,} total passwords")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./ultra-import.py <wordlist.txt> [source_name]")
        print("\nExample:")
        print("  ./ultra-import.py ~/Downloads/weakpass_4.txt weakpass_4")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    asyncio.run(ultra_import(filepath, source))
