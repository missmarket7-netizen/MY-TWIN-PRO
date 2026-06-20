"""Memory Lifecycle – TTL, Compression, Summarization, Archiving."""
import logging
from datetime import datetime, timezone, timedelta
from app.memory.memory_service import save as save_memory
from app.memory.memory_extractor import generate_summary
from app.repositories.memory_repository import get_recent, delete_older_than, count

logger = logging.getLogger("memory_lifecycle")

async def process_memory_lifecycle(user_id: str) -> Dict[str, Any]:
    """Process memory lifecycle: compress old memories, archive very old ones."""
    total = await count(user_id)
    if total < 50:
        return {"status": "ok", "message": "Not enough memories to process"}
    
    recent = await get_recent(user_id, 100)
    result = {"compressed": 0, "archived": 0, "deleted": 0}
    
    # Archive memories older than 90 days
    archived = await delete_older_than([user_id], 90)
    result["archived"] = archived
    
    # Compress memories older than 30 days
    old_memories = [m for m in recent if hasattr(m, 'created_at') and (datetime.now(timezone.utc) - datetime.fromisoformat(m.created_at)).days > 30]
    if old_memories:
        summary = await generate_summary([{"role": "memory", "content": m.content} for m in old_memories[:20]])
        if summary:
            await save_memory(user_id=user_id, content=f"[ملخص] {summary}", memory_type="summary", importance=0.9)
            result["compressed"] = len(old_memories)
            for m in old_memories[:20]:
                try:
                    from app.repositories.memory_repository import delete_memory
                    await delete_memory(m.id)
                except:
                    pass
            result["deleted"] = len(old_memories[:20])
    
    logger.info(f"Memory lifecycle processed for {user_id}: {result}")
    return result
