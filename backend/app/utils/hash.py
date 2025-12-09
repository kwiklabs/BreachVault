import hashlib
import re


def is_valid_sha256(hash_value: str) -> bool:
    """Check if a string is a valid SHA-256 hash"""
    return bool(re.match(r'^[a-f0-9]{64}$', hash_value.lower()))


def sha256(text: str) -> str:
    """Generate SHA-256 hash from text"""
    return hashlib.sha256(text.encode()).hexdigest()


def normalize_hash(hash_value: str) -> str:
    """Normalize hash to lowercase"""
    return hash_value.lower().strip()


def process_breach_file_line(line: str) -> str | None:
    """Process a line from a breach file and return normalized hash"""
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Skip comments
    if line.startswith('#'):
        return None

    # If line contains a colon (email:password format), hash the password part
    if ':' in line:
        _, password = line.split(':', 1)
        return sha256(password)

    # If it's already a hash, validate and return it
    if is_valid_sha256(line):
        return normalize_hash(line)

    # Otherwise, hash the line as a password
    return sha256(line)
