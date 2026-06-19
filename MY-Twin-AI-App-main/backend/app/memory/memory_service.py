"""Memory Service – orchestrates all memory operations (store, retrieve, summarize)."""
import logging
from typing import List, Optional
from app.repositories.memory_repository import (
    store_memory as repo_store,
    search_similar,
    get_recent,
    count,
    delete_old,
)
from app.models.memory import Memory

logger = logging.getLogger("memory_service")

MAX_MEMORIES = 100

async def save(user_id: str, content: str, memory_type: str = "daily",
               importance: float = 0.5, emotion: str = None) -> Optional[str]:
    """Save a memory with auto‑pruning."""
    mem = Memory(user_id=user_id, content=content, memory_type=memory_type,
                 importance=importance, emotion=emotion)
    memory_id = await repo_store(mem)
    if memory_id:
        await delete_old(user_id, MAX_MEMORIES)
        logger.info(f"💾 Memory saved: {content[:60]}...")
    return memory_id


async def retrieve(query_embedding: List[float], user_id: str,
                   top_k: int = 5, threshold: float = 0.55) -> List[Memory]:
    """Semantic search for relevant memories."""
    return await search_similar(query_embedding, user_id, top_k, threshold)


async def get_recent_memories(user_id: str, limit: int = 10) -> List[Memory]:
    """Get most recent memories."""
    return await get_recent(user_id, limit)


async def get_memory_count(user_id: str) -> int:
    """Total memories for a user."""
    return await count(user_id)


async def delete_oldest(user_id: str, keep: int = MAX_MEMORIES) -> int:
    """Prune oldest memories."""
    return await delete_old(user_id, keep)
