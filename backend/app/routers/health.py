from fastapi import APIRouter
from app.models import HealthResponse, StatsResponse
from app.services.db import db_service
from app.services.cache import cache_service
from app.services.bloom import bloom_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    db_healthy = await db_service.health_check()
    redis_healthy = await cache_service.health_check()
    bloom_healthy = bloom_service.initialized

    return HealthResponse(
        status="healthy" if all([db_healthy, redis_healthy, bloom_healthy]) else "degraded",
        database="up" if db_healthy else "down",
        redis="up" if redis_healthy else "down",
        bloom_filter="initialized" if bloom_healthy else "not initialized"
    )


@router.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics
    """
    db_stats = await db_service.get_stats()
    cache_stats = await cache_service.get_stats()
    bloom_stats = bloom_service.get_stats()

    return StatsResponse(
        total_hashes=db_stats["total_hashes"],
        sources=db_stats["sources"],
        bloom_filter_size=bloom_stats.get("size", 0),
        redis_keys=cache_stats["redis_keys"]
    )
