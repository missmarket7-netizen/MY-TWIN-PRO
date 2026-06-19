"""Security utilities – JWT decoding."""
import os, logging
from typing import Optional
import jwt
from jwt.exceptions import PyJWTError

logger = logging.getLogger("security")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

def decode_access_token(token: str) -> Optional[dict]:
    if not token or not SUPABASE_JWT_SECRET:
        logger.error("Missing token or SUPABASE_JWT_SECRET")
        return None
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated", options={"verify_exp": True, "verify_aud": True})
        return payload
    except PyJWTError as e:
        logger.error(f"JWT decode failed: {e}")
        return None

def extract_user_id(payload: dict) -> Optional[str]:
    return payload.get("sub") or payload.get("user_id") or None
