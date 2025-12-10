#!/usr/bin/env python3
"""
Simple sequential processor - one chunk at a time, delete when done
No parallel complexity, just pure speed with bloom filter
"""
import sys
import hashlib
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime
import pickle
import glob

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'user': 'breachvault',
    'password': 'breachvault123',
    'database': 'breachvault'
}
BATCH_SIZE = 100_000
CHUNK_DIR = Path.home() / "Downloads" / "weakpass_chunks"

# Load bloom filter once
print("Loading bloom filter...")
with open("/tmp/breach_bloom_filter.pkl", 'rb') as f:
    bloom = pickle.load(f)
print(f"✅ Bloom filter loaded\n")

# Connect once
conn = psycopg2.connect(**DB_PARAMS)
conn.autocommit = False
cur = conn.cursor()
cur.execute("SET synchronous_commit = OFF")
conn.commit()

total_processed = 0
total_inserted = 0
start_time = datetime.now()

while True:
    # Find next chunk
    chunks = sorted(glob.glob(str(CHUNK_DIR / "chunk_*.txt")))
    if not chunks:
        print("\n✅ All chunks complete!")
        break
    
    chunk_file = Path(chunks[0])
    print(f"\n[{chunk_file.name}] Processing...")
    
    batch = []
    chunk_total = 0
    chunk_skipped = 0
    chunk_start = datetime.now()
    
    with open(chunk_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            h = hashlib.sha256(password.encode()).hexdigest()
            chunk_total += 1
            
            # Bloom filter check
            if h in bloom:
                chunk_skipped += 1
                continue
            
            batch.append((h, 'weakpass_4'))
            
            if len(batch) >= BATCH_SIZE:
                execute_values(
                    cur,
                    "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
                    batch,
                    page_size=BATCH_SIZE
                )
                conn.commit()
                batch = []
    
    # Final batch
    if batch:
        execute_values(
            cur,
            "INSERT INTO breached_hashes (hash, source) VALUES %s ON CONFLICT (hash) DO NOTHING",
            batch
        )
        conn.commit()
    
    chunk_elapsed = (datetime.now() - chunk_start).total_seconds()
    skip_pct = (chunk_skipped / chunk_total * 100) if chunk_total > 0 else 0
    speed = chunk_total / chunk_elapsed if chunk_elapsed > 0 else 0
    
    total_processed += chunk_total
    total_inserted += (chunk_total - chunk_skipped)
    
    print(f"[{chunk_file.name}] ✅ {chunk_total:,} | Skipped: {skip_pct:.1f}% | {speed:,.0f}/s | {chunk_elapsed:.1f}s")
    
    # DELETE chunk
    chunk_file.unlink()
    
    # Progress
    elapsed = (datetime.now() - start_time).total_seconds()
    avg_speed = total_processed / elapsed if elapsed > 0 else 0
    print(f"Overall: {total_processed:,} processed | {avg_speed:,.0f}/s avg")

cur.close()
conn.close()

elapsed = (datetime.now() - start_time).total_seconds()
print(f"\n🏆 Complete: {total_processed:,} processed, {total_inserted:,} new in {elapsed:.1f}s")
