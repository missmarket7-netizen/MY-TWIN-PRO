"""Background tasks – relationship update, memory save, reflection, cleanup."""
import logging
from typing import Dict, List, Optional
from app.infrastructure.queue.background import enqueue

logger = logging.getLogger("background_tasks")

async def schedule_post_reply(user_id: str, message: str, reply: str, history: List[Dict] = None, twin_name: str = "توأمك", emotion: Dict = None, context_data: Dict = None) -> None:
    """Schedule all post‑reply background tasks."""
    await enqueue("update_relationship", _update_relationship, user_id, message, emotion, context_data)
    await enqueue("save_memory", _save_memory, user_id, message, reply, history, twin_name)
    await enqueue("reflect", _reflect, user_id, message, twin_name)
    await enqueue("cleanup_memories", _cleanup_memories, user_id)

async def _update_relationship(user_id: str, message: str, emotion: Dict = None, context_data: Dict = None):
    from app.domain.services.relationship_service import update_relationship
    await update_relationship(user_id=user_id, emotion=emotion, message=message, journey_phase=context_data.get("journey",{}).get("phase") if context_data else None, attachment_style=context_data.get("attachment",{}).get("style") if context_data else None)

async def _save_memory(user_id: str, message: str, reply: str, history: List[Dict] = None, twin_name: str = "توأمك"):
    try:
        from app.memory_summarizer import memory_summarizer
        await memory_summarizer.increment_counter(user_id)
        if await memory_summarizer.should_summarize(user_id):
            msgs = (history or [])[-50:] + [{"role":"user","content":message},{"role":"twin","content":reply[:500]}]
            await memory_summarizer.summarize_and_store(user_id, msgs)
    except Exception as e: logger.warning(f"Memory save failed: {e}")

async def _reflect(user_id: str, message: str, twin_name: str = "توأمك"):
    try:
        from app.consciousness_core import consciousness_core
        await consciousness_core.reflect(user_id, message[:200], "ar")
    except Exception as e: logger.warning(f"Reflection failed: {e}")

async def _cleanup_memories(user_id: str):
    try:
        from app.infrastructure.cache.memory_cleanup_service import run_memory_cleanup
        await run_memory_cleanup(dry=False)
    except Exception as e: logger.warning(f"Cleanup failed: {e}")
