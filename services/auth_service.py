"""
Password security and hashing utilities module for TypeMaster.
Provides iterations, pbkdf2 key derivation, salting, and constant-time verify checks.
"""
import hashlib
import hmac
import os
import logging

logger = logging.getLogger("services.auth_service")

# NIST recommended minimum iterations for PBKDF2 with SHA-256
PBKDF2_ITERATIONS = 100000

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256.
    Generates a secure random 16-byte salt.
    Returns format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )
    salt_hex = salt.hex()
    hash_hex = derived_key.hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_hex}${hash_hex}"

def verify_password(password: str, hashed_value: str) -> bool:
    """
    Verifies a password against its PBKDF2-HMAC-SHA256 hash.
    Performs parsing validation and constant-time string comparison.
    """
    if not hashed_value or not isinstance(hashed_value, str):
        return False
        
    parts = hashed_value.split('$')
    if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
        logger.warning("Attempted to verify password with unrecognized hash format.")
        return False
        
    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
    except ValueError as err:
        logger.error(f"Failed to parse database password hash components: {err}")
        return False
        
    # Reconstruct the candidate hash using the same iterations and salt
    candidate_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    
    # Timing-attacker resistant equality check
    return hmac.compare_digest(candidate_hash, expected_hash)
