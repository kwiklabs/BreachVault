from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PasswordCheckRequest(BaseModel):
    hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 hash of the password")


class PasswordCheckResponse(BaseModel):
    breached: bool
    source: Optional[str] = None
    timestamp: Optional[datetime] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ImportRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)


class ImportResponse(BaseModel):
    imported: int
    skipped: int
    total: int
    source: str


class StatsResponse(BaseModel):
    total_hashes: int
    sources: list[str]
    bloom_filter_size: int
    redis_keys: int


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    bloom_filter: str
