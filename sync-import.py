#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Ultra-Simple Sync Import
No async, no multiprocessing complications, just pure speed
"""
import sys
import hashlib
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'user': 'breachvault',
    'password': 'breachvault123',
    'database': 'breachvault'
}
BATCH_SIZE = 50_000

def main():
    if len(sys.argv) < 2:
        print("Usage: ./sync-import.py <wordlist> [source]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    print("═" * 70)
    print("  DATASEED MASTER-9000: Sync Import")
    print("═" * 70)
    print()
    print(f"📂 File: {filepath.name}")
    print(f"💾 Batch: {BATCH_SIZE:,}")
    print()
    
    # Connect
    print("🔌 Connecting...")
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = False
    cur = conn.cursor()
    
    # Optimize
    cur.execute("SET synchronous_commit = OFF")
    conn.commit()
    
    print("✅ Connected!")
    print()
    print("🚀 Starting import...")
    print()
    
    batch = []
    total = 0
    inserted = 0
    start = datetime.now()
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            # Hash
            h = hashlib.sha256(password.encode()).hexdigest()
            batch.append((h, source))
            total += 1
            
            # Insert batch
            if len(batch) >= BATCH_SIZE:
                try:
                    execute_values(
                        cur,
                        "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
                        batch,
                        page_size=BATCH_SIZE
                    )
                    conn.commit()
                    inserted += cur.rowcount if cur.rowcount > 0 else 0
                    
                    elapsed = (datetime.now() - start).total_seconds()
                    speed = total / elapsed if elapsed > 0 else 0
                    
                    print(f"📥 {total:,} | New: {inserted:,} | {speed:,.0f}/s | {elapsed:.0f}s")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    conn.rollback()
                
                batch = []
    
    # Last batch
    if batch:
        try:
            execute_values(
                cur,
                "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
                batch,
                page_size=len(batch)
            )
            conn.commit()
            inserted += cur.rowcount if cur.rowcount > 0 else 0
        except Exception as e:
            print(f"❌ Error: {e}")
    
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print()
    print("═" * 70)
    print("  ✅ COMPLETE")
    print("═" * 70)
    print(f"Processed: {total:,}")
    print(f"Inserted: {inserted:,}")
    print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if elapsed > 0:
        print(f"Speed: {total/elapsed:,.0f}/s")

if __name__ == "__main__":
    main()
