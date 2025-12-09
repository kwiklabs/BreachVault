from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from app.models import ImportResponse
from app.dependencies import verify_token
from app.services.db import db_service
from app.services.bloom import bloom_service
from app.services.cache import cache_service
from app.utils.hash import process_breach_file_line
import asyncio
import hashlib
import tempfile
import os

router = APIRouter(prefix="/api/v1", tags=["Import"])

# File validation settings
MAX_FILE_SIZE = 100 * 1024 * 1024 * 1024  # 100GB
ALLOWED_EXTENSIONS = {'.txt', '.lst', '.dic', '.wordlist'}


def validate_breach_file(filename: str, content: bytes) -> tuple[bool, str]:
    """
    Validate uploaded breach file
    Returns (is_valid, error_message)
    """
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE // (1024**3)}GB"
    
    # Check if file is text
    try:
        sample = content[:10000].decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        return False, "File must be UTF-8 text"
    
    # Check for suspicious content
    if any(keyword in sample.lower() for keyword in ['<script', '<?php', 'DROP TABLE']):
        return False, "Suspicious content detected"
    
    # Verify it contains password-like data
    lines = sample.split('\n')[:100]
    valid_lines = sum(1 for line in lines if line.strip() and 3 <= len(line.strip()) <= 500)
    
    if valid_lines < 10:
        return False, "File doesn't appear to contain valid password data"
    
    return True, ""


async def process_import_background(filepath: str, source: str):
    """Process import in background"""
    import subprocess
    
    # Call the optimized seed script
    result = subprocess.run(
        ['python', '/app/scripts/seed_rockyou.py', filepath, source],
        capture_output=True,
        text=True
    )
    
    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)
    
    return result.returncode == 0


@router.post("/import", response_model=ImportResponse)
async def import_breach_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = Form(...),
    _: dict = Depends(verify_token)
):
    """
    Import a breach file (Admin only)
    - Validates file format and content
    - Processes in background for large files
    - Automatically detects and skips duplicates
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # Read and validate file
    content = await file.read()
    
    is_valid, error_msg = validate_breach_file(file.filename, content)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # For large files (>10MB), process in background
    if len(content) > 10 * 1024 * 1024:
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Process in background
        background_tasks.add_task(process_import_background, tmp_path, source)
        
        return ImportResponse(
            imported=0,
            skipped=0,
            total=0,
            source=source,
            message="Large file queued for background processing. Check stats page for progress."
        )

    # For small files, process immediately
    imported = 0
    skipped = 0
    total = 0

    try:
        lines = content.decode('utf-8', errors='ignore').splitlines()

        # Process hashes in batches
        batch_size = 1000
        batch = []

        for line in lines:
            total += 1
            hash_value = process_breach_file_line(line)

            if hash_value:
                batch.append(hash_value)

                if len(batch) >= batch_size:
                    # Process batch
                    batch_imported, batch_skipped = await process_batch(batch, source)
                    imported += batch_imported
                    skipped += batch_skipped
                    batch = []

        # Process remaining batch
        if batch:
            batch_imported, batch_skipped = await process_batch(batch, source)
            imported += batch_imported
            skipped += batch_skipped

        return ImportResponse(
            imported=imported,
            skipped=skipped,
            total=total,
            source=source
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


async def process_batch(hashes: list[str], source: str) -> tuple[int, int]:
    """Process a batch of hashes"""
    imported = 0
    skipped = 0

    for hash_value in hashes:
        # Try to insert into database
        success = await db_service.insert_hash(hash_value, source)

        if success:
            # Add to bloom filter
            bloom_service.add(hash_value)
            imported += 1
        else:
            skipped += 1

    return imported, skipped
