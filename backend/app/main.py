from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.services.db import db_service
from app.services.cache import cache_service
from app.services.bloom import bloom_service
from app.middleware import RateLimitMiddleware, LoggingMiddleware
from app.routers import auth, check, import_router, chunk_router, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    print("🚀 Starting BreachVault...")

    # Connect to services
    await db_service.connect()
    await cache_service.connect()

    # Initialize bloom filter with existing hashes
    print("📊 Loading existing hashes into Bloom Filter...")
    existing_hashes = await db_service.get_all_hashes()
    bloom_service.initialize(existing_hashes)

    print(f"✅ BreachVault started successfully with {len(existing_hashes)} hashes")

    yield

    # Shutdown
    print("🛑 Shutting down BreachVault...")
    await db_service.disconnect()
    await cache_service.disconnect()
    print("✅ BreachVault shut down gracefully")


# Create FastAPI app
app = FastAPI(
    title="BreachVault API",
    description="Ultra-fast password breach checker with Bloom Filter → Redis → PostgreSQL cascade",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(check.router)
app.include_router(import_router)
app.include_router(chunk_router)


@app.get("/")
async def root():
    return {
        "message": "BreachVault API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
