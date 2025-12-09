from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://breachvault:breachvault123@localhost:5432/breachvault"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "supersecretchangeme"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Admin credentials
    admin_username: str = "admin"
    admin_password: str = "changeme2025"

    # Bloom filter settings
    bloom_filter_capacity: int = 100_000_000
    bloom_filter_error_rate: float = 0.001

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Redis cache TTL (seconds)
    cache_ttl: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
