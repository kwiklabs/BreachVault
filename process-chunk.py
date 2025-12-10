#!/usr/bin/env python3
"""
Process one chunk file - designed to be run in parallel
NOW WITH BLOOM FILTER: Skip duplicates before touching DB!
"""
import sys
import hashlib
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime
import pickle

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'user': 'breachvault',
    'password': 'breachvault123',
    'database': 'breachvault'
}
BATCH_SIZE = 100_000

def process_chunk(filepath, source):
    print(f"[{filepath.name}] Starting...", flush=True)
    
    # Load bloom filter
    bloom_file = "/tmp/breach_bloom_filter.pkl"
    if Path(bloom_file).exists():
        print(f"[{filepath.name}] Loading bloom filter...", flush=True)
        with open(bloom_file, 'rb') as f:
            bloom = pickle.load(f)
        print(f"[{filepath.name}] Bloom filter loaded (will skip ~98% duplicates)", flush=True)
    else:
        print(f"[{filepath.name}] No bloom filter found - processing all", flush=True)
        bloom = None
    
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET synchronous_commit = OFF")
    conn.commit()
    
    batch = []
    total = 0
    skipped = 0
    start = datetime.now()
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            h = hashlib.sha256(password.encode()).hexdigest()
            total += 1
            
            # BLOOM FILTER CHECK - skip if likely duplicate
            if bloom and h in bloom:
                skipped += 1
                continue
            
            batch.append((h, source))
            
            if len(batch) >= BATCH_SIZE:
                execute_values(
                    cur,
                    "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
                    batch,
                    page_size=BATCH_SIZE
                )
                conn.commit()
                
                elapsed = (datetime.now() - start).total_seconds()
                speed = total / elapsed if elapsed > 0 else 0
                skip_pct = (skipped / total * 100) if total > 0 else 0
                print(f"[{filepath.name}] {total:,} | {speed:,.0f}/s | Skipped: {skip_pct:.1f}%")
                
                batch = []
    
    # Final batch
    if batch:
        execute_values(
            cur,
            "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
            batch,
            page_size=len(batch)
        )
        conn.commit()
    
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start).total_seconds()
    skip_pct = (skipped / total * 100) if total > 0 else 0
    print(f"[{filepath.name}] ✅ Complete: {total:,} processed, {skipped:,} skipped ({skip_pct:.1f}%), {elapsed:.1f}s")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./process-chunk.py <chunk_file> [source]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else "weakpass_4"
    
    process_chunk(filepath, source)
