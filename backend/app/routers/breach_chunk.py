"""
Streaming chunk upload API for breach files
Processes passwords in real-time without storing full file
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.dependencies import verify_token
import asyncio
import hashlib
from typing import Dict, Set
import time
from app.services.db import get_db_pool

router = APIRouter(prefix="/api/breach/chunk", tags=["breach-chunk-upload"])

# In-memory session tracking
upload_sessions: Dict[str, dict] = {}
SESSION_TIMEOUT = 3600  # 1 hour

# Session structure:
# {
#   "upload_id": {
#     "filename": str,
#     "total_chunks": int,
#     "processed_chunks": Set[int],
#     "hashes_processed": int,
#     "duplicates_skipped": int,
#     "started_at": float,
#     "last_activity": float,
#     "status": "active" | "completed" | "error",
#     "error_message": str | None,
#     "batch_buffer": List[str],  # Accumulate hashes for batch insert
#   }
# }


async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    current_time = time.time()
    expired_sessions = [
        upload_id
        for upload_id, session in upload_sessions.items()
        if current_time - session["last_activity"] > SESSION_TIMEOUT
    ]
    for upload_id in expired_sessions:
        del upload_sessions[upload_id]


async def process_password_chunk(
    chunk_data: bytes, upload_id: str, source: str = "admin_upload"
) -> dict:
    """
    Process a chunk of passwords:
    1. Decode text
    2. Hash each password
    3. Add to batch buffer
    4. Insert batch when buffer is full
    """
    session = upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    try:
        # Decode chunk as text
        text = chunk_data.decode("utf-8", errors="ignore")
        lines = text.split("\n")

        # Remove empty lines and whitespace
        passwords = [line.strip() for line in lines if line.strip()]

        # Hash passwords
        hashes = []
        for password in passwords:
            if password:  # Skip empty lines
                # SHA-256 hash
                hash_obj = hashlib.sha256(password.encode("utf-8"))
                password_hash = hash_obj.hexdigest()
                hashes.append(password_hash)

        # Add to batch buffer
        session["batch_buffer"].extend(hashes)
        session["hashes_processed"] += len(hashes)

        # Insert batch if buffer is large enough (10k hashes)
        BATCH_SIZE = 10000
        if len(session["batch_buffer"]) >= BATCH_SIZE:
            await flush_batch_buffer(upload_id, source)

        session["last_activity"] = time.time()

        return {
            "hashes_in_chunk": len(hashes),
            "total_hashes_processed": session["hashes_processed"],
            "buffer_size": len(session["batch_buffer"]),
        }

    except Exception as e:
        session["status"] = "error"
        session["error_message"] = str(e)
        raise HTTPException(status_code=500, detail=f"Error processing chunk: {str(e)}")


async def flush_batch_buffer(upload_id: str, source: str):
    """
    Flush the batch buffer to database
    Uses ON CONFLICT DO NOTHING to handle duplicates
    """
    session = upload_sessions.get(upload_id)
    if not session or not session["batch_buffer"]:
        return

    pool = await get_db_pool()
    batch = session["batch_buffer"]
    batch_size = len(batch)

    try:
        # Prepare batch insert with ON CONFLICT DO NOTHING
        insert_query = """
            INSERT INTO breached_hashes (hash, source)
            VALUES ($1, $2)
            ON CONFLICT (hash) DO NOTHING
        """

        # Create list of tuples for executemany
        records = [(hash_val, source) for hash_val in batch]

        async with pool.acquire() as conn:
            # Execute batch insert
            await conn.executemany(insert_query, records)

        # Clear buffer
        session["batch_buffer"] = []

        # Note: We don't track duplicates_skipped because ON CONFLICT DO NOTHING
        # doesn't return which rows were skipped

    except Exception as e:
        session["status"] = "error"
        session["error_message"] = f"Database error: {str(e)}"
        raise


@router.post("/start")
async def start_upload_session(
    filename: str = Form(...),
    total_chunks: int = Form(...),
    file_size: int = Form(...),
    _=verify_token,
):
    """
    Initialize a new chunked upload session
    """
    # Generate upload ID
    upload_id = f"{int(time.time())}_{hashlib.sha256(filename.encode()).hexdigest()[:16]}"

    # Create session
    upload_sessions[upload_id] = {
        "filename": filename,
        "total_chunks": total_chunks,
        "file_size": file_size,
        "processed_chunks": set(),
        "hashes_processed": 0,
        "duplicates_skipped": 0,
        "started_at": time.time(),
        "last_activity": time.time(),
        "status": "active",
        "error_message": None,
        "batch_buffer": [],
    }

    return {
        "upload_id": upload_id,
        "status": "initialized",
        "message": f"Upload session created for {filename}",
    }


@router.post("/upload")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    chunk: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    _=verify_token,
):
    """
    Upload and process a single chunk
    Processes passwords in real-time without storing the full file
    """
    # Verify session exists
    session = upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    # Check if chunk already processed (for resume capability)
    if chunk_index in session["processed_chunks"]:
        return {
            "status": "already_processed",
            "chunk_index": chunk_index,
            "total_hashes_processed": session["hashes_processed"],
        }

    # Read chunk data
    chunk_data = await chunk.read()

    # Process the chunk (hash passwords and batch insert)
    result = await process_password_chunk(
        chunk_data, upload_id, source=session["filename"]
    )

    # Mark chunk as processed
    session["processed_chunks"].add(chunk_index)

    # Check if this is the last chunk
    is_last_chunk = len(session["processed_chunks"]) == total_chunks

    if is_last_chunk:
        # Flush any remaining hashes in buffer
        await flush_batch_buffer(upload_id, source=session["filename"])
        session["status"] = "completed"

        # Schedule cleanup in background
        if background_tasks:
            background_tasks.add_task(cleanup_completed_session, upload_id)

    return {
        "status": "processed",
        "chunk_index": chunk_index,
        "chunks_completed": len(session["processed_chunks"]),
        "total_chunks": total_chunks,
        "progress": (len(session["processed_chunks"]) / total_chunks) * 100,
        "hashes_in_chunk": result["hashes_in_chunk"],
        "total_hashes_processed": result["total_hashes_processed"],
        "buffer_size": result["buffer_size"],
        "is_complete": is_last_chunk,
    }


@router.get("/status/{upload_id}")
async def get_upload_status(upload_id: str, _=verify_token):
    """
    Get status of an upload session
    """
    session = upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    return {
        "upload_id": upload_id,
        "filename": session["filename"],
        "status": session["status"],
        "total_chunks": session["total_chunks"],
        "processed_chunks": len(session["processed_chunks"]),
        "progress": (len(session["processed_chunks"]) / session["total_chunks"]) * 100,
        "hashes_processed": session["hashes_processed"],
        "buffer_size": len(session["batch_buffer"]),
        "elapsed_time": time.time() - session["started_at"],
        "error_message": session.get("error_message"),
    }


@router.post("/cancel/{upload_id}")
async def cancel_upload(upload_id: str, _=verify_token):
    """
    Cancel an upload session
    """
    session = upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session["status"] = "cancelled"
    del upload_sessions[upload_id]

    return {"status": "cancelled", "upload_id": upload_id}


async def cleanup_completed_session(upload_id: str):
    """
    Background task to cleanup completed session after a delay
    """
    await asyncio.sleep(300)  # Keep session info for 5 minutes
    if upload_id in upload_sessions:
        del upload_sessions[upload_id]
