#!/usr/bin/env python3
"""
Optimized seed script to import rockyou.txt or other breach files into BreachVault
Uses PostgreSQL COPY and asyncio for maximum performance
Usage: python seed_rockyou_fast.py <file_path> <source_name>
"""

import asyncio
import sys
import os
import hashlib
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncpg
from app.config import get_settings


async def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.strip().encode('utf-8')).hexdigest()


async def seed_from_file_fast(file_path: str, source: str):
    """Optimized seed using COPY command and bulk operations"""
    print(f"🚀 Fast seeding from {file_path} (source: {source})")
    
    settings = get_settings()
    db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Connect to database
    conn = await asyncpg.connect(db_url)
    
    try:
        # Prepare temp file for COPY
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_path = temp_file.name
        
        print(f"📝 Processing passwords and writing to temp file...")
        total_lines = 0
        unique_hashes = set()
        
        # Read file and hash passwords
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                total_lines += 1
                password = line.strip()
                
                if password and len(password) > 0:
                    # Hash the password
                    hash_value = await hash_password(password)
                    
                    if hash_value not in unique_hashes:
                        unique_hashes.add(hash_value)
                        # Write to temp file: hash, source, timestamp
                        temp_file.write(f"{hash_value}\t{source}\t{datetime.now().isoformat()}\n")
                
                if total_lines % 100000 == 0:
                    print(f"  Processed {total_lines:,} lines... ({len(unique_hashes):,} unique hashes)")
        
        temp_file.close()
        
        print(f"\n✅ Processed {total_lines:,} lines")
        print(f"📊 Found {len(unique_hashes):,} unique hashes")
        print(f"\n🗄️  Importing to database in batches...")
        
        # Convert set to list for batching
        hash_list = list(unique_hashes)
        batch_size = 10000
        imported = 0
        skipped = 0
        
        for i in range(0, len(hash_list), batch_size):
            batch = hash_list[i:i + batch_size]
            
            # Use executemany for batch insert with ON CONFLICT
            try:
                await conn.executemany(
                    "INSERT INTO breached_hashes (hash, source, created_at) VALUES ($1, $2, $3) ON CONFLICT (hash) DO NOTHING",
                    [(h, source, datetime.now()) for h in batch]
                )
                imported += len(batch)
                
                if (i + batch_size) % 100000 == 0:
                    print(f"  Imported {imported:,} / {len(hash_list):,} hashes...")
            except Exception as e:
                print(f"  Error in batch {i}: {e}")
                skipped += len(batch)
        
        print(f"\n✅ Import complete!")
        print(f"  Total lines read: {total_lines:,}")
        print(f"  Unique hashes: {len(unique_hashes):,}")
        print(f"  Imported: {imported:,}")
        
        # Clean up temp file
        os.unlink(temp_path)
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_rockyou_fast.py <file_path> [source_name]")
        print("Example: python seed_rockyou_fast.py /data/rockyou.txt rockyou")
        sys.exit(1)

    file_path = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(file_path)

    asyncio.run(seed_from_file_fast(file_path, source))
