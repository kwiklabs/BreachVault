from pybloom_live import BloomFilter
from app.config import get_settings
from typing import Optional


class BloomFilterService:
    def __init__(self):
        self.bloom: Optional[BloomFilter] = None
        self.settings = get_settings()
        self.initialized = False

    def initialize(self, existing_hashes: list[str] = None):
        """Initialize bloom filter with existing hashes"""
        self.bloom = BloomFilter(
            capacity=self.settings.bloom_filter_capacity,
            error_rate=self.settings.bloom_filter_error_rate
        )

        if existing_hashes:
            for hash_value in existing_hashes:
                self.bloom.add(hash_value)

        self.initialized = True
        print(f"Bloom filter initialized with {len(existing_hashes or [])} hashes")

    def add(self, hash_value: str):
        """Add a hash to the bloom filter"""
        if not self.initialized:
            raise RuntimeError("Bloom filter not initialized")
        self.bloom.add(hash_value)

    def check(self, hash_value: str) -> bool:
        """Check if hash might be in the set (may have false positives)"""
        if not self.initialized:
            raise RuntimeError("Bloom filter not initialized")
        return hash_value in self.bloom

    def get_stats(self) -> dict:
        """Get bloom filter statistics"""
        if not self.initialized:
            return {
                "initialized": False,
                "size": 0,
                "capacity": self.settings.bloom_filter_capacity,
                "error_rate": self.settings.bloom_filter_error_rate
            }

        return {
            "initialized": True,
            "size": self.bloom.count,
            "capacity": self.settings.bloom_filter_capacity,
            "error_rate": self.settings.bloom_filter_error_rate,
            "fill_rate": self.bloom.count / self.settings.bloom_filter_capacity
        }


# Global bloom filter instance
bloom_service = BloomFilterService()
