#!/usr/bin/env python3
"""
Google-scale approach: Build bloom filter from existing DB hashes
Then filter all input files through it before inserting
"""
import sys
import psycopg2
from pybloom_live import BloomFilter
import pickle

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'user': 'breachvault',
    'password': 'breachvault123',
    'database': 'breachvault'
}

print("Building bloom filter from existing database...")
print()

# Connect
conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# Get count
cur.execute("SELECT COUNT(*) FROM breached_hashes")
count = cur.fetchone()[0]
print(f"Found {count:,} existing hashes")

# Create bloom filter (0.1% false positive rate)
bf = BloomFilter(capacity=count, error_rate=0.001)

print("Loading hashes into bloom filter...")
cur.execute("SELECT hash FROM breached_hashes")

loaded = 0
for row in cur:
    bf.add(row[0])
    loaded += 1
    if loaded % 1_000_000 == 0:
        print(f"  Loaded {loaded:,} / {count:,}")

cur.close()
conn.close()

print(f"\n✅ Loaded {loaded:,} hashes")
print(f"Bloom filter size: {len(bf.bitarray) / (8 * 1024 * 1024):.1f} MB")

# Save to file
output_file = "/tmp/breach_bloom_filter.pkl"
with open(output_file, 'wb') as f:
    pickle.dump(bf, f)

print(f"\n💾 Saved to: {output_file}")
print("\nNow use this filter in process-chunk.py to skip duplicates!")
