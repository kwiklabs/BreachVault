#!/usr/bin/env python3
"""
DATASEED MASTER-9000: Fixed Parallel Import
Simple multiprocessing with proper queue handling
"""
import sys
import hashlib
import asyncpg
import asyncio
from pathlib import Path
from multiprocessing import Process, Queue, cpu_count
from datetime import datetime
import signal

DB_URL = "postgresql://breachvault:breachvault123@localhost:5433/breachvault"
BATCH_SIZE = 10_000  # Smaller batches for faster feedback
NUM_WORKERS = 10

def worker(worker_id, queue, source):
    """Worker process - consume passwords from queue and insert"""
    async def run():
        try:
            # Connect to DB
            conn = await asyncpg.connect(DB_URL)
            await conn.execute("SET synchronous_commit = OFF")
            
            batch = []
            total = 0
            
            while True:
                try:
                    item = queue.get()
                except:
                    break
                
                # Check for stop signal
                if item is None:
                    break
                
                # Hash password
                password_hash = hashlib.sha256(item.encode('utf-8', errors='ignore')).hexdigest()
                batch.append((password_hash, source))
                
                # Insert when batch full
                if len(batch) >= BATCH_SIZE:
                    try:
                        await conn.executemany(
                            "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                            batch
                        )
                        total += len(batch)
                        # Report progress
                        if total % 50000 == 0:
                            print(f"Worker {worker_id}: {total:,} processed")
                    except Exception as e:
                        print(f"Worker {worker_id}: ERROR - {e}")
                        # Retry smaller batches on error
                        for single in batch:
                            try:
                                await conn.execute(
                                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                                    single[0], single[1]
                                )
                                total += 1
                            except:
                                pass
                    batch = []
            
            # Final batch
            if batch:
                try:
                    await conn.executemany(
                        "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                        batch
                    )
                    total += len(batch)
                except:
                    for single in batch:
                        try:
                            await conn.execute(
                                "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2) ON CONFLICT (hash) DO NOTHING",
                                single[0], single[1]
                            )
                            total += 1
                        except:
                            pass
            
            await conn.close()
        except Exception as e:
            pass  # Silent worker exit
    
    asyncio.run(run())

def main():
    if len(sys.argv) < 2:
        print("Usage: ./fixed-turbo.py <wordlist> [source]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    source = sys.argv[2] if len(sys.argv) > 2 else filepath.stem
    
    print("═" * 70)
    print("  DATASEED MASTER-9000: Fixed Parallel Import")
    print("═" * 70)
    print()
    print(f"📂 File: {filepath.name}")
    print(f"⚙️  Workers: {NUM_WORKERS}")
    print(f"💾 Batch size: {BATCH_SIZE:,}")
    print()
    
    # Create queue - bigger queue to buffer more work
    queue = Queue(maxsize=10000)  # Increased from 1000
    
    # Start workers
    print("🚀 Starting workers...")
    workers = []
    for i in range(NUM_WORKERS):
        p = Process(target=worker, args=(i, queue, source))
        p.start()
        workers.append(p)
        print(f"  ✅ Worker {i} started (PID: {p.pid})")
    
    print()
    print("📖 Reading file and distributing work...")
    print()
    
    # Read file and feed queue
    count = 0
    start = datetime.now()
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if password:
                    # Use timeout to avoid blocking forever
                    try:
                        queue.put(password, timeout=1)
                        count += 1
                        
                        if count % 100_000 == 0:
                            elapsed = (datetime.now() - start).total_seconds()
                            speed = count / elapsed if elapsed > 0 else 0
                            qsize = queue.qsize()
                            print(f"📥 Queued: {count:,} | Speed: {speed:,.0f}/s | Queue: {qsize:,}")
                    except:
                        # Queue full, wait a bit
                        print(f"⏸️  Queue full at {count:,}, waiting for workers...")
                        queue.put(password)  # Blocking put
                        count += 1
        
        print()
        print(f"✅ Finished reading {count:,} passwords")
        print("⏳ Sending stop signals to workers...")
        
        # Send poison pills
        for _ in range(NUM_WORKERS):
            queue.put(None)
        
        # Wait for workers
        print("⏳ Waiting for workers to finish...")
        for i, p in enumerate(workers):
            p.join()
            print(f"  ✅ Worker {i} finished")
        
        elapsed = (datetime.now() - start).total_seconds()
        
        print()
        print("═" * 70)
        print("  🏆 IMPORT COMPLETE")
        print("═" * 70)
        print(f"✅ Processed: {count:,} passwords")
        print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        if elapsed > 0:
            print(f"⚡ Speed: {count/elapsed:,.0f} passwords/sec")
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted! Stopping workers...")
        for p in workers:
            p.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
