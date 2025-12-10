#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Hash-to-Pipe Engine
Write hashes to stdout, pipe directly to psql COPY
This is THE FASTEST method for bulk PostgreSQL inserts

Usage:
  ./hash-to-stdout.py ~/Downloads/weakpass_4.txt weakpass_4 | \\
    PGPASSWORD=breachvault123 psql -h localhost -p 5433 -U breachvault -d breachvault \\
    -c "COPY breached_hashes (password_hash, source) FROM STDIN WITH (FORMAT TEXT, DELIMITER E'\\t')"
"""

import sys
import hashlib
from datetime import datetime

class Stats:
    def __init__(self):
        self.count = 0
        self.start = datetime.now()
        self.last_report = self.start
    
    def update(self):
        self.count += 1
        if self.count % 100000 == 0:
            now = datetime.now()
            elapsed = (now - self.start).total_seconds()
            speed = self.count / elapsed if elapsed > 0 else 0
            print(f"[{self.count:,} | {speed:,.0f}/s]", file=sys.stderr, flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./hash-to-stdout.py <file> <source>", file=sys.stderr)
        print("\nPipe to psql COPY for maximum speed:", file=sys.stderr)
        print("  ./hash-to-stdout.py rockyou.txt rockyou | \\", file=sys.stderr)
        print("    PGPASSWORD=pass psql -h host -U user -d db -c \"COPY ...\"", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    source = sys.argv[2]
    
    print(f"Hashing {filepath}...", file=sys.stderr)
    
    stats = Stats()
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"{password_hash}\t{source}")  # To stdout for pipe
            stats.update()
    
    elapsed = (datetime.now() - stats.start).total_seconds()
    print(f"\nDone: {stats.count:,} in {elapsed:.1f}s ({stats.count/elapsed:,.0f}/s)", 
          file=sys.stderr)
