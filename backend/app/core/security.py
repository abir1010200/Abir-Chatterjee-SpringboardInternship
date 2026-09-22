import os
import hmac
import hashlib
import base64
import json
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

# Secret key for token signing (can be overridden via environment variable)
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "krishipals-ai-super-secure-token-secret-2026")
ACCESS_TOKEN_EXPIRE_DAYS = 7
DEFAULT_DEMO_PASSWORD = "krishi123"

def hash_password(plain_password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        plain_password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    ).hex()
    return f"{salt}:{pw_hash}"

def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Verify password against stored salt:hash or accept demo default if not set."""
    if not hashed_password:
        # Backward compatibility for seeded demo farmers
        return plain_password == DEFAULT_DEMO_PASSWORD

    try:
        salt, stored_hash = hashed_password.split(":")
        calc_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100_000
        ).hex()
        return hmac.compare_digest(stored_hash, calc_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create HMAC-SHA256 signed tamper-proof access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": int(expire.timestamp())})
    payload_bytes = json.dumps(to_encode, sort_keys=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")

    signature = hmac.new(
        AUTH_SECRET_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{signature}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify signature and return token payload if valid and not expired."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts

        # Verify signature
        expected_sig = hmac.new(
            AUTH_SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        # Add base64 padding if needed
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)

        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None

        return payload
    except Exception:
        return None
