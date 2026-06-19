"""Singleton Supabase client – the ONLY file that imports supabase-py."""
import os, logging
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
_db: Client | None = None

def get_db() -> Client:
    global _db
    if _db is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")
        _db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase client initialized")
    return _db

async def get_profile(user_id: str) -> dict:
    db = get_db()
    try:
        result = db.table("profiles").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Failed to fetch profile: {e}")
        return {}
