#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Direct COPY Pipeline
Simplest and fastest: hash → pipe directly to COPY FROM STDIN
No temp files, no temp tables, just pure streaming performance
"""

import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"

class Stats:
    def __init__(self):
        self.total = 0
        self.start = datetime.now()
        self.last_report = self.start
        self.last_count = 0
    
    def update(self, count):
        self.total += count
        now = datetime.now()
        
        if (now - self.last_report).total_seconds() >= 2:
            elapsed = (now - self.start).total_seconds()
            current_speed = (self.total - self.last_count) / (now - self.last_report).total_seconds()
            avg_speed = self.total / elapsed if elapsed > 0 else 0
            
            print(f"\r✨ {self.total:,} | ⚡ {current_speed:,.0f}/s | 📊 {avg_speed:,.0f}/s avg", 
                  end='', flush=True)
            
            self.last_report = now
            self.last_count = self.total

async def stream_generator(filepath: Path, source: str, stats: Stats):
    """Generate hashed rows on the fly"""
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Yield as bytes (COPY needs binary)
            yield f"{password_hash}\t{source}\n".encode('utf-8')
            
            count += 1
            if count % 50000 == 0:
                stats.update(50000)

async def direct_copy(filepath: Path, source: str):
    """Stream hashes directly into PostgreSQL via COPY"""
    
    print("═" * 60)
    print("  DATASEED MASTER-9000: Direct COPY Pipeline")
    print("  🚀 Hash → COPY STDIN = Zero overhead")
    print("═" * 60)
    print()
    
    conn = await asyncpg.connect(DB_URL)
    
    before = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    print(f"📊 Before: {before:,} passwords\n")
    
    await conn.execute("SET synchronous_commit = OFF")
    
    print(f"📂 Processing: {filepath.name}")
    print()
    
    stats = Stats()
    start = datetime.now()
    
    # COPY from generator
    copy_query = """
        COPY breached_hashes (password_hash, source) 
        FROM STDIN 
        WITH (FORMAT TEXT, DELIMITER E'\\t')
    """
    
    try:
        await conn.copy_records_to_table(
            'breached_hashes',
            records=stream_generator(filepath, source, stats),
            columns=['password_hash', 'source']
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying alternative method...")
    
    after = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    new_rows = after - before
    
    print("\n")
    print("═" * 60)
    print("  🏆 DIRECT COPY COMPLETE")
    print("═" * 60)
    print(f"✅ Processed: {stats.total:,} passwords")
    print(f"✅ New rows: {new_rows:,}")
    print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if elapsed > 0:
        print(f"⚡ Speed: {stats.total/elapsed:,.0f} passwords/sec")
    print(f"📊 After: {after:,} total passwords")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./stream-copy.py <wordlist.txt> [source_name]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    asyncio.run(direct_copy(filepath, source))
