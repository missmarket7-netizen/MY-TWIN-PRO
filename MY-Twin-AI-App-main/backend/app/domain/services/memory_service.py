"""Memory Service – semantic retrieval for chat."""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("memory_service")

try:
    from app.memory_retriever import memory_retriever
except ImportError:
    memory_retriever = None

async def retrieve_memories(query: str, user_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
    if not memory_retriever:
        return []
    try:
        result = await memory_retriever.retrieve_and_summarize(query, user_id, top_k)
        return result.get("memories", [])
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")
        return []

async def get_memory_context(query: str, user_id: str) -> str:
    memories = await retrieve_memories(query, user_id)
    if not memories:
        return ""
    lines = ["<MEMORIES>"]
    for m in memories[:3]:
        lines.append(f"- {m.get('content', '')[:200]}")
    lines.append("</MEMORIES>")
    return "\n".join(lines)
