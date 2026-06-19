"""Memory Repository – semantic memories with pgvector."""
import logging
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db
from app.models.memory import Memory

logger = logging.getLogger(__name__)
TABLE = "memory_embeddings"


async def store_memory(user_id: str, content: str, memory_type: str = "daily",
                       importance: float = 0.5, emotion: Optional[str] = None,
                       embedding: Optional[List[float]] = None, org_id: Optional[str] = None) -> Optional[str]:
    db = get_db()
    try:
        r = db.table(TABLE).insert({
            "user_id": user_id,
            "content": content,
            "embedding": embedding,
            "memory_type": memory_type,
            "importance": importance,
            "emotion": emotion,
        }).execute()
        return r.data[0]["id"] if r.data else None
    except Exception as e:
        logger.error(f"store_memory failed: {e}")
        return None


async def search_similar(query_embedding: List[float], user_id: str,
                         top_k: int = 5, threshold: float = 0.55) -> List[Memory]:
    db = get_db()
    try:
        r = db.rpc("match_memory_embeddings", {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": top_k,
            "p_user_id": user_id,
        }).execute()
        if r.data:
            return [Memory(id=m["id"], user_id=user_id, content=m["content"],
                         memory_type=m.get("memory_type","daily"),
                         importance=m.get("importance",0.5),
                         scores={"similarity": m.get("similarity",0)},
                         is_hard=m.get("memory_type")=="core") for m in r.data]
        return []
    except Exception as e:
        logger.error(f"search_similar failed: {e}")
        return []


async def get_recent(user_id: str, limit: int = 10) -> List[Memory]:
    db = get_db()
    try:
        r = db.table(TABLE).select("id,content,memory_type,importance,emotion,created_at")\
            .eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        if r.data:
            return [Memory(id=m["id"], user_id=user_id, content=m["content"],
                         memory_type=m.get("memory_type","daily"),
                         importance=m.get("importance",0.5),
                         emotion=m.get("emotion")) for m in r.data]
        return []
    except:
        return []


async def count(user_id: str) -> int:
    db = get_db()
    try:
        r = db.table(TABLE).select("*", count="exact").eq("user_id", user_id).execute()
        return r.count or 0
    except:
        return 0


async def delete_old(user_id: str, keep: int = 100) -> int:
    db = get_db()
    try:
        total = await count(user_id)
        if total <= keep: return 0
        r = db.table(TABLE).select("id").eq("user_id", user_id).order("created_at", asc=True).limit(total - keep).execute()
        if r.data:
            ids = [row["id"] for row in r.data]
            db.table(TABLE).delete().in_("id", ids).execute()
            return len(ids)
        return 0
    except:
        return 0


async def delete_older_than(user_ids: List[str], days: int) -> int:
    db = get_db()
    try:
        cut = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = db.table(TABLE).delete().in_("user_id", user_ids).lt("created_at", cut).execute()
        return len(r.data) if r.data else 0
    except:
        return 0
