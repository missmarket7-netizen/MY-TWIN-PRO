"""
Raw Conversation Archive - Layer 1 of TCMA.
Stores every interaction without any filtering.
Supports Arabic and Western contexts equally.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("raw_archive")

TABLE_NAME = "raw_conversation_archive"

async def archive_message(
    user_id: str,
    message: str,
    role: str,
    emotion: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
    conversation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Archive a single message with full context.
    Nothing is lost. Everything is preserved.
    """
    db = get_db()
    try:
        payload = {
            "user_id": user_id,
            "content": message,
            "role": role,  # user / twin
            "emotion_primary": emotion.get("primary") if emotion else None,
            "emotion_intensity": emotion.get("intensity") if emotion else None,
            "detected_intent": intent,
            "conversation_id": conversation_id,
            "language": "ar" if any("\u0600" <= c <= "\u06ff" for c in message) else "en",
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = db.table(TABLE_NAME).insert(payload).execute()
        return result.data[0]["id"] if result.data else ""
    except Exception as e:
        logger.error(f"Failed to archive message: {e}")
        return ""


async def get_conversation_archive(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Retrieve raw conversation archive."""
    db = get_db()
    try:
        result = (
            db.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to retrieve archive: {e}")
        return []
