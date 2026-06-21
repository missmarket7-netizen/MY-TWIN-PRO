"""
Background Tasks v3.0 – متكاملة مع TCMA والمحركات الجديدة + Event Bus
==========================================================================
تستبدل الخدمات القديمة بطبقات TCMA والمحركات الاستباقية.
"""
import logging
from typing import Dict, List, Optional
from app.background.queue import enqueue

logger = logging.getLogger("background_tasks")

async def schedule_post_reply(
    user_id: str,
    message: str,
    reply: str,
    history: List[Dict] = None,
    twin_name: str = "توأمك",
    emotion: Dict = None,
    context_data: Dict = None
) -> None:
    """جدولة مهام ما بعد الرد - تستخدم TCMA الجديدة"""
    
    await enqueue("update_relationship", _update_relationship, user_id, message, emotion, context_data)
    await enqueue("save_emotional_memory", _save_emotional_memory, user_id, message)
    await enqueue("process_reflections", _process_reflections, user_id, message)
    await enqueue("update_identity", _update_identity, user_id, message)
    await enqueue("proactive_check", _proactive_check, user_id)
    await enqueue("emit_event", _emit_chat_event, user_id, message, reply, emotion)

async def _update_relationship(user_id: str, message: str, emotion: Dict = None, context_data: Dict = None):
    try:
        from app.twin_state.relationship_service import update_relationship
        await update_relationship(
            user_id=user_id, emotion=emotion, message=message,
            journey_phase=context_data.get("journey",{}).get("phase") if context_data else None,
            attachment_style=context_data.get("attachment",{}).get("style") if context_data else None
        )
    except Exception as e:
        logger.warning(f"Relationship update failed: {e}")

async def _save_emotional_memory(user_id: str, message: str):
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=user_id, expressed_text=message[:300],
            detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.0},
            trigger="chat", cultural_context="محادثة عامة"
        )
    except Exception as e:
        logger.warning(f"Emotional memory save failed: {e}")

async def _process_reflections(user_id: str, message: str):
    try:
        from app.memory.reflection.reflection_engine import process_message_for_reflections
        await process_message_for_reflections(
            user_id=user_id, message=message[:200], language="ar", detected_emotion="neutral"
        )
    except Exception as e:
        logger.warning(f"Reflection failed: {e}")

async def _update_identity(user_id: str, message: str):
    try:
        from app.memory.identity.identity_model import analyze_and_update_identity
        await analyze_and_update_identity(user_id=user_id, message=message[:200], language="ar")
    except Exception as e:
        logger.warning(f"Identity update failed: {e}")

async def _proactive_check(user_id: str):
    try:
        from app.features.proactive_engine import proactive_engine
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        profile = db.table("profiles").select("last_active").eq("id", user_id).single().execute()
        if profile.data and profile.data.get("last_active"):
            from datetime import datetime, timezone, timedelta
            last = datetime.fromisoformat(profile.data["last_active"].replace("Z", "+00:00"))
            hours_since = (datetime.now(timezone.utc) - last).total_seconds() / 3600
            if hours_since >= 18:
                await proactive_engine.generate_proactive_message(user_id)
                logger.info(f"📨 Proactive message for {user_id}")
    except Exception as e:
        logger.warning(f"Proactive check failed: {e}")

async def _emit_chat_event(user_id: str, message: str, reply: str, emotion: Dict = None):
    """إرسال حدث محادثة إلى Event Bus"""
    try:
        from app.events.event_bus import emit
        await emit({
            "type": "message_received",
            "user_id": user_id,
            "content": message[:200],
            "reply": reply[:200],
            "emotion": emotion.get("primary", "neutral") if emotion else "neutral"
        })
    except Exception as e:
        logger.warning(f"Event emit failed: {e}")

logger.info("✅ Background Tasks v3.0 with TCMA + Event Bus")
