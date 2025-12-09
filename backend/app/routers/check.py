from fastapi import APIRouter, HTTPException, status
from app.models import PasswordCheckRequest, PasswordCheckResponse
from app.services.bloom import bloom_service
from app.services.cache import cache_service
from app.services.db import db_service
from app.utils.hash import is_valid_sha256, normalize_hash

router = APIRouter(prefix="/api/v1", tags=["Check"])


@router.post("/check", response_model=PasswordCheckResponse)
async def check_password(request: PasswordCheckRequest):
    """
    Check if a password hash has been breached
    Uses cascading lookup: Bloom Filter → Redis → PostgreSQL
    """
    # Validate hash format
    if not is_valid_sha256(request.hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hash format. Must be a valid SHA-256 hash (64 hex characters)"
        )

    hash_value = normalize_hash(request.hash)

    # Step 1: Check Bloom Filter (fast negative check)
    if not bloom_service.check(hash_value):
        # Definitely not in the database
        return PasswordCheckResponse(breached=False)

    # Step 2: Check Redis Cache
    cache_key = f"breach:{hash_value}"
    cached_result = await cache_service.get(cache_key)

    if cached_result is not None:
        if cached_result.get("breached"):
            return PasswordCheckResponse(
                breached=True,
                source=cached_result.get("source"),
                timestamp=cached_result.get("timestamp")
            )
        else:
            return PasswordCheckResponse(breached=False)

    # Step 3: Check PostgreSQL Database
    db_result = await db_service.check_hash(hash_value)

    if db_result:
        # Cache the positive result
        await cache_service.set(cache_key, {
            "breached": True,
            "source": db_result["source"],
            "timestamp": db_result["timestamp"].isoformat()
        })

        return PasswordCheckResponse(
            breached=True,
            source=db_result["source"],
            timestamp=db_result["timestamp"]
        )
    else:
        # Cache the negative result (but with shorter TTL to handle false positives)
        await cache_service.set(cache_key, {"breached": False}, ttl=3600)

        return PasswordCheckResponse(breached=False)
