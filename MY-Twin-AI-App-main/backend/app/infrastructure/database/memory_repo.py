"""Memory repository – pgvector-based semantic memory storage and retrieval."""
import logging
from typing import List, Optional, Dict, Any
from app.infrastructure.database.supabase_client import get_db
from app.infrastructure.ai.embedding_client import generate_embedding

logger = logging.getLogger("memory_repo")

MEMORY_TABLE = "memory_embeddings"
TOP_K = 5
SIMILARITY_THRESHOLD = 0.55


async def store_memory(
    user_id: str,
    content: str,
    memory_type: str = "conversation_summary",
    importance: float = 0.5,
) -> Optional[str]:
    """
    Store a memory with its embedding vector.
    Returns the new memory ID.
    """
    db = get_db()
    embedding = await generate_embedding(content)
    
    if not embedding:
        return None

    try:
        result = db.table(MEMORY_TABLE).insert({
            "user_id": user_id,
            "content": content,
            "embedding": embedding,
            "memory_type": memory_type,
            "importance": importance,
        }).execute()

        return result.data[0]["id"] if result.data else None
    except Exception as e:
        logger.error(f"Failed to store memory for user {user_id}: {e}")
        return None


async def search_memories(
    user_id: str,
    query_text: str,
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Semantic search for memories using vector similarity.
    Returns top_k most similar memories above threshold.
    """
    db = get_db()
    query_embedding = await generate_embedding(query_text)
    
    if not query_embedding:
        return []

    try:
        result = db.rpc(
            "match_memory_embeddings",
            {
                "query_embedding": query_embedding,
                "match_threshold": SIMILARITY_THRESHOLD,
                "match_count": top_k,
                "p_user_id": user_id,
            },
        ).execute()

        if result.data:
            return [
                {
                    "id": r["id"],
                    "content": r["content"],
                    "similarity": r.get("similarity", 0),
                    "memory_type": r.get("memory_type", ""),
                    "importance": r.get("importance", 0.5),
                }
                for r in result.data
            ]
        return []
    except Exception as e:
        logger.error(f"Memory search failed for user {user_id}: {e}")
        return []


async def get_recent_memories(
    user_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Get most recent memories for a user."""
    db = get_db()
    try:
        result = db.table(MEMORY_TABLE)\
            .select("id,content,memory_type,importance,created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to fetch recent memories: {e}")
        return []


async def count_memories(user_id: str) -> int:
    """Count total memories for a user."""
    db = get_db()
    try:
        result = db.table(MEMORY_TABLE)\
            .select("*", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        return result.count or 0
    except Exception:
        return 0


async def delete_old_memories(user_id: str, keep: int = 100) -> int:
    """Delete oldest memories, keeping only the most recent `keep`."""
    db = get_db()
    try:
        count = await count_memories(user_id)
        if count <= keep:
            return 0

        to_delete = count - keep
        old = db.table(MEMORY_TABLE)\
            .select("id")\
            .eq("user_id", user_id)\
            .order("created_at", asc=True)\
            .limit(to_delete)\
            .execute()

        if old.data:
            ids = [r["id"] for r in old.data]
            db.table(MEMORY_TABLE).delete().in_("id", ids).execute()
            return len(ids)
        return 0
    except Exception as e:
        logger.error(f"Failed to delete old memories: {e}")
        return 0
