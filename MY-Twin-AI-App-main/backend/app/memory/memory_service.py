"""Memory Service – Complete with ranking, compression, and lifecycle."""
import logging
from typing import List, Optional, Dict, Any
from app.repositories.memory_repository import (
    store_memory as repo_store,
    search_similar,
    get_recent,
    count,
    delete_old,
)
from app.memory.memory_ranker import rank
from app.memory.memory_extractor import generate_summary, should_summarize, increment_counter, reset_counter
from app.models.memory import Memory

logger = logging.getLogger("memory_service")

MAX_MEMORIES = 100

async def save(user_id: str, content: str, memory_type: str = "daily",
               importance: float = 0.5, emotion: str = None) -> Optional[str]:
    """Save memory with auto-pruning and lifecycle management."""
    mem = Memory(user_id=user_id, content=content, memory_type=memory_type,
                 importance=importance, emotion=emotion)
    memory_id = await repo_store(mem)
    if memory_id:
        await delete_old(user_id, MAX_MEMORIES)
        logger.info(f"💾 Memory saved: {content[:60]}...")
    return memory_id

async def retrieve(query_embedding: List[float], user_id: str,
                   top_k: int = 5, threshold: float = 0.55) -> List[Memory]:
    """Semantic search with ranking."""
    memories = await search_similar(query_embedding, user_id, top_k, threshold)
    return rank(memories) if memories else []

async def get_recent_memories(user_id: str, limit: int = 10) -> List[Memory]:
    """Get recent memories with ranking."""
    memories = await get_recent(user_id, limit)
    return rank(memories) if memories else []

async def get_memory_count(user_id: str) -> int:
    """Total memories for a user."""
    return await count(user_id)

async def delete_oldest(user_id: str, keep: int = MAX_MEMORIES) -> int:
    """Prune oldest memories."""
    return await delete_old(user_id, keep)

async def process_conversation_summary(user_id: str, messages: List[Dict[str, str]]) -> Optional[str]:
    """Summarize conversation and store as memory."""
    await increment_counter(user_id)
    if not await should_summarize(user_id):
        return None
    
    summary = await generate_summary(messages)
    if summary:
        await save(user_id, content=summary, memory_type="conversation_summary", importance=0.8)
        await reset_counter(user_id)
    return summary

async def get_memory_context(user_id: str, message: str, top_k: int = 3) -> str:
    """Build context string from relevant memories."""
    memories = await get_recent_memories(user_id, top_k * 2)
    if not memories:
        return ""
    
    # Simple keyword relevance scoring
    query_words = set(message.lower().split())
    scored = []
    for m in memories:
        content_words = set(m.content.lower().split())
        overlap = len(query_words & content_words)
        if overlap > 0:
            scored.append((overlap, m))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    relevant = [m for _, m in scored[:top_k]]
    
    if not relevant:
        return ""
    
    lines = ["<MEMORIES>"]
    for m in relevant:
        lines.append(f"- {m.content[:200]}")
    lines.append("</MEMORIES>")
    return "\n".join(lines)
