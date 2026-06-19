"""Background tasks – with Proactive Telegram notifications."""
import logging
from typing import Dict, List, Optional
from app.background.queue import enqueue
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("background_tasks")

async def schedule_post_reply(user_id: str, message: str, reply: str, history: List[Dict] = None, twin_name: str = "توأمك", emotion: Dict = None, context_data: Dict = None) -> None:
    """جدولة مهام ما بعد الرد."""
    await enqueue("update_relationship", _update_relationship, user_id, message, emotion, context_data)
    await enqueue("save_memory", _save_memory, user_id, message, reply, history, twin_name)
    await enqueue("reflect", _reflect, user_id, message, twin_name)
    await enqueue("cleanup_memories", _cleanup_memories, user_id)
    await enqueue("proactive_telegram", _send_proactive_telegram_if_needed, user_id)

async def _update_relationship(user_id: str, message: str, emotion: Dict = None, context_data: Dict = None):
    from app.twin_state.relationship_service import update_relationship
    await update_relationship(user_id=user_id, emotion=emotion, message=message, journey_phase=context_data.get("journey",{}).get("phase") if context_data else None, attachment_style=context_data.get("attachment",{}).get("style") if context_data else None)

async def _save_memory(user_id: str, message: str, reply: str, history: List[Dict] = None, twin_name: str = "توأمك"):
    try:
        from app.memory.memory_service import save
        await save(user_id=user_id, content=f"محادثة: {message[:300]}", memory_type="conversation", importance=0.6)
    except Exception as e:
        logger.warning(f"Memory save failed: {e}")

async def _reflect(user_id: str, message: str, twin_name: str = "توأمك"):
    try:
        from app.twin_state.consciousness_service import reflect
        await reflect(user_id, message[:200], twin_name, "ar")
    except Exception as e:
        logger.warning(f"Reflection failed: {e}")

async def _cleanup_memories(user_id: str):
    try:
        from app.infrastructure.cache.memory_cleanup_service import run_memory_cleanup
        await run_memory_cleanup(dry=False)
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

async def _send_proactive_telegram_if_needed(user_id: str):
    """إرسال رسالة استباقية عبر تيليجرام إذا كان المستخدم غير نشط."""
    try:
        from app.infrastructure.integrations.telegram_webhook import send_proactive_telegram
        from app.repositories.profile_repository import get_profile
        from app.twin_state.journey_service import get_daily_message, get_phase
        from app.twin_state.relationship_service import load as load_relationship
        
        profile = await get_profile(user_id)
        if not profile:
            return
        
        telegram_chat_id = profile.get("telegram_chat_id")
        if not telegram_chat_id:
            return
        
        # التحقق من آخر نشاط
        last_active = profile.get("last_active")
        if last_active:
            from datetime import datetime, timezone, timedelta
            last = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            hours_since = (now - last).total_seconds() / 3600
            
            if hours_since < 18:  # لم يمضِ وقت كافٍ
                return
        
        lang = profile.get("lang", "ar")
        relationship = await load_relationship(user_id)
        phase = await get_phase(relationship.bond_level)
        message = await get_daily_message(phase, lang)
        
        await send_proactive_telegram(user_id, message, telegram_chat_id)
        logger.info(f"📨 Proactive Telegram sent to {user_id}")
    except Exception as e:
        logger.warning(f"Proactive Telegram failed: {e}")
