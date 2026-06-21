"""Goals Repository v2.0 – أهداف المستخدم (Supabase مباشر)"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger(__name__)

async def get_active(user_id: str) -> List[Dict[str, Any]]:
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("priority", desc=True).execute()
        return r.data or []
    except: return []

async def get_completed(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).eq("status", "completed").order("updated_at", desc=True).limit(limit).execute()
        return r.data or []
    except: return []

async def create(user_id: str, title: str, progress: float = 0.0, priority: int = 1, status: str = "active") -> Optional[str]:
    db = get_db()
    try:
        r = db.table("goals").insert({
            "user_id": user_id, "title": title, "progress": progress,
            "priority": priority, "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return r.data[0]["id"] if r.data else None
    except: return None

async def update_progress(goal_id: str, progress: float) -> None:
    db = get_db()
    try:
        db.table("goals").update({"progress": progress, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", goal_id).execute()
    except: pass

async def complete(goal_id: str) -> None:
    db = get_db()
    try:
        db.table("goals").update({"status": "completed", "progress": 100.0, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", goal_id).execute()
    except: pass

async def count_active(user_id: str) -> int:
    db = get_db()
    try:
        r = db.table("goals").select("*", count="exact").eq("user_id", user_id).eq("status", "active").execute()
        return r.count or 0
    except: return 0

logger.info("✅ Goals Repository v2.0")
