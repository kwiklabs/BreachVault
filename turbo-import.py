#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Ultra-fast parallel password importer
Targets: 500K-1M inserts/sec on modern hardware
"""
import asyncio
import asyncpg
import hashlib
import sys
import time
from pathlib import Path
from multiprocessing import Process, Queue, cpu_count
from typing import Optional

# Configuration
DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
BATCH_SIZE = 200_000  # Doubled for more throughput
WORKERS = cpu_count()  # Use all cores
QUEUE_SIZE = 10  # Increased buffer

class Stats:
    def __init__(self):
        self.total = 0
        self.start = time.time()
        self.last_report = time.time()
        self.last_count = 0
    
    def update(self, count):
        self.total += count
        now = time.time()
        if now - self.last_report >= 1.0:
            elapsed = now - self.start
            rate = self.total / elapsed if elapsed > 0 else 0
            recent_rate = (self.total - self.last_count) / (now - self.last_report)
            
            print(f"\r⚡ {self.total:,} passwords | "
                  f"Avg: {rate:,.0f}/s | "
                  f"Current: {recent_rate:,.0f}/s | "
                  f"⏱️  {elapsed:.0f}s", 
                  end="", flush=True)
            
            self.last_report = now
            self.last_count = self.total

async def batch_insert(conn, batch, source):
    """Optimized batch insert with ON CONFLICT"""
    await conn.executemany(
        """
        INSERT INTO breached_hashes (hash, source) 
        VALUES ($1, $2) 
        ON CONFLICT (hash) DO NOTHING
        """,
        batch
    )

async def worker_process(worker_id: int, queue: Queue, source: str, stats_queue: Queue):
    """Worker: consume chunks from queue, hash, batch insert"""
    conn = await asyncpg.connect(DB_URL)
    
    # Set connection optimization
    await conn.execute("SET synchronous_commit = OFF")
    await conn.execute("SET work_mem = '256MB'")
    
    batch = []
    local_count = 0
    
    try:
        while True:
            chunk = queue.get()
            if chunk is None:  # Poison pill
                break
            
            for line in chunk:
                password = line.strip()
                if not password:
                    continue
                
                password_hash = hashlib.sha256(password.encode('utf-8', errors='ignore')).hexdigest()
                batch.append((password_hash, source))
                
                if len(batch) >= BATCH_SIZE:
                    await batch_insert(conn, batch, source)
                    local_count += len(batch)
                    stats_queue.put(len(batch))
                    batch = []
        
        # Flush remaining
        if batch:
            await batch_insert(conn, batch, source)
            local_count += len(batch)
            stats_queue.put(len(batch))
    
    finally:
        await conn.close()

def worker_wrapper(worker_id, queue, source, stats_queue):
    """Wrapper to run async worker in separate process"""
    asyncio.run(worker_process(worker_id, queue, source, stats_queue))

def stats_collector(stats_queue):
    """Collect stats from all workers"""
    stats = Stats()
    while True:
        try:
            count = stats_queue.get(timeout=0.1)
            if count is None:
                break
            stats.update(count)
        except:
            continue
    
    print()  # Newline after progress
    elapsed = time.time() - stats.start
    print(f"\n✅ Completed: {stats.total:,} passwords in {elapsed:.1f}s ({stats.total/elapsed:,.0f}/sec)")

async def import_file(filepath: str, source: str, workers: int = WORKERS):
    """Main import orchestrator"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    print(f"📂 Importing: {filepath.name}")
    print(f"⚙️  Workers: {workers}")
    print(f"⚙️  Batch size: {BATCH_SIZE:,}")
    print()
    
    # Create queues
    work_queue = Queue(maxsize=workers * QUEUE_SIZE)
    stats_queue = Queue()
    
    # Start workers
    processes = []
    for i in range(workers):
        p = Process(target=worker_wrapper, args=(i, work_queue, source, stats_queue))
        p.start()
        processes.append(p)
    
    # Start stats collector
    stats_proc = Process(target=stats_collector, args=(stats_queue,))
    stats_proc.start()
    
    # Feed file to workers in chunks
    chunk_size = 10_000
    chunk = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                chunk.append(line)
                if len(chunk) >= chunk_size:
                    work_queue.put(chunk)
                    chunk = []
            
            # Send remaining
            if chunk:
                work_queue.put(chunk)
        
        # Send poison pills
        for _ in range(workers):
            work_queue.put(None)
        
        # Wait for workers
        for p in processes:
            p.join()
        
        # Stop stats
        stats_queue.put(None)
        stats_proc.join()
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted! Cleaning up...")
        for p in processes:
            p.terminate()
        stats_proc.terminate()

async def get_db_count():
    """Get current password count"""
    conn = await asyncpg.connect(DB_URL)
    count = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
    await conn.close()
    return count

async def main():
    if len(sys.argv) < 2:
        print("Usage: ./turbo-import.py <wordlist.txt> [source_name]")
        print("\nExample:")
        print("  ./turbo-import.py ~/Downloads/rockyou.txt rockyou")
        print("  WORKERS=32 ./turbo-import.py crackstation.txt crackstation")
        sys.exit(1)
    
    filepath = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else Path(filepath).stem
    
    # Override workers from env
    import os
    workers = int(os.getenv('WORKERS', WORKERS))
    
    print("═" * 60)
    print("  DATASEED MASTER-9000: Turbo Import Engine")
    print("═" * 60)
    print()
    
    # Show before count
    before = await get_db_count()
    print(f"📊 Database before: {before:,} passwords\n")
    
    # Import
    await import_file(filepath, source, workers)
    
    # Show after count
    after = await get_db_count()
    print(f"📊 Database after: {after:,} passwords")
    print(f"📈 Imported: {after - before:,} new passwords")
    print()

if __name__ == "__main__":
    asyncio.run(main())
