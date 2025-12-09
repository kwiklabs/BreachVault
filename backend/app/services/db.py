import asyncpg
from app.config import get_settings
from typing import Optional, List
from datetime import datetime


class DatabaseService:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.settings = get_settings()

    async def connect(self):
        """Initialize database connection pool"""
        # Remove the postgresql+asyncpg:// prefix for asyncpg
        db_url = self.settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

        self.pool = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        await self.create_tables()

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()

    async def create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS breached_hashes (
                    hash TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Create index for faster lookups
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_breached_hashes_source
                ON breached_hashes(source)
            """)

    async def check_hash(self, hash_value: str) -> Optional[dict]:
        """Check if a hash exists in the database"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT hash, source, created_at FROM breached_hashes WHERE hash = $1",
                hash_value
            )
            if row:
                return {
                    "hash": row["hash"],
                    "source": row["source"],
                    "timestamp": row["created_at"]
                }
            return None

    async def insert_hash(self, hash_value: str, source: str) -> bool:
        """Insert a hash into the database (returns False if already exists)"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2)",
                    hash_value, source
                )
                return True
            except asyncpg.UniqueViolationError:
                return False

    async def bulk_insert_hashes(self, hashes: List[str], source: str) -> tuple[int, int]:
        """Bulk insert hashes, returns (imported, skipped)"""
        imported = 0
        skipped = 0

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for hash_value in hashes:
                    try:
                        await conn.execute(
                            "INSERT INTO breached_hashes (hash, source) VALUES ($1, $2)",
                            hash_value, source
                        )
                        imported += 1
                    except asyncpg.UniqueViolationError:
                        skipped += 1

        return imported, skipped

    async def get_all_hashes(self) -> List[str]:
        """Get all hashes from database (for bloom filter initialization)"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT hash FROM breached_hashes")
            return [row["hash"] for row in rows]

    async def get_stats(self) -> dict:
        """Get database statistics"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM breached_hashes")
            sources = await conn.fetch("SELECT DISTINCT source FROM breached_hashes")

            return {
                "total_hashes": total,
                "sources": [row["source"] for row in sources]
            }

    async def health_check(self) -> bool:
        """Check if database is healthy"""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False


# Global database instance
db_service = DatabaseService()
