"""Goals Repository – active objectives, progress tracking, completed."""
import logging
from typing import List, Optional
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.models.goal import Goal

logger = logging.getLogger(__name__)

async def get_active(user_id: str) -> List[Goal]:
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("priority", desc=True).execute()
        if r.data:
            return [Goal(id=g["id"], user_id=user_id, title=g["title"],
                         progress=g.get("progress",0), priority=g.get("priority",1),
                         status=g.get("status","active")) for g in r.data]
        return []
    except: return []

async def get_completed(user_id: str, limit: int = 10) -> List[Goal]:
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).eq("status", "completed")\
            .order("updated_at", desc=True).limit(limit).execute()
        if r.data:
            return [Goal(id=g["id"], user_id=user_id, title=g["title"],
                         progress=100.0, priority=g.get("priority",1),
                         status="completed") for g in r.data]
        return []
    except: return []

async def create(goal: Goal) -> Optional[str]:
    db = get_db()
    try:
        r = db.table("goals").insert({
            "user_id": goal.user_id, "title": goal.title,
            "progress": goal.progress, "priority": goal.priority, "status": goal.status,
        }).execute()
        return r.data[0]["id"] if r.data else None
    except: return None

async def update_progress(goal_id: str, progress: float) -> None:
    db = get_db()
    try:
        db.table("goals").update({"progress": progress, "updated_at": datetime.now(timezone.utc).isoformat()})\
            .eq("id", goal_id).execute()
    except: pass

async def complete(goal_id: str) -> None:
    db = get_db()
    try:
        db.table("goals").update({
            "status": "completed", "progress": 100.0,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", goal_id).execute()
    except: pass

async def abandon(goal_id: str) -> None:
    db = get_db()
    try:
        db.table("goals").update({
            "status": "abandoned", "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", goal_id).execute()
    except: pass

async def count_active(user_id: str) -> int:
    db = get_db()
    try:
        r = db.table("goals").select("*", count="exact").eq("user_id", user_id).eq("status", "active").execute()
        return r.count or 0
    except: return 0
