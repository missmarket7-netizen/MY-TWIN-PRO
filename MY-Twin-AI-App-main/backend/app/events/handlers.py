"""Event Handlers – with Proactive Telegram notifications."""
import logging
from app.models.event import (
    BaseEvent, StageChangeEvent, MemoryEvent, TrustEvent,
    GoalEvent, AttachmentEvent, ReflectionEvent, EventType,
)
from app.events.event_bus import subscribe

logger = logging.getLogger("event_handlers")

async def on_stage_changed(event: BaseEvent) -> None:
    if not isinstance(event, StageChangeEvent): return
    logger.info(f"🎉 Stage up: {event.old_stage} → {event.new_stage}")
    # إرسال إشعار تيليجرام عند تغيير المرحلة
    try:
        from app.infrastructure.integrations.telegram_webhook import send_proactive_telegram
        from app.repositories.profile_repository import get_profile
        profile = await get_profile(event.user_id)
        if profile:
            telegram_chat_id = profile.get("telegram_chat_id")
            if telegram_chat_id:
                lang = profile.get("lang", "ar")
                if lang == "ar":
                    await send_proactive_telegram(event.user_id, event.message_ar, telegram_chat_id)
                else:
                    await send_proactive_telegram(event.user_id, event.message_en, telegram_chat_id)
    except Exception as e:
        logger.warning(f"Telegram proactive failed: {e}")

subscribe(EventType.STAGE_CHANGED.value, on_stage_changed)

async def on_memory_created(event: BaseEvent) -> None:
    if not isinstance(event, MemoryEvent): return
    logger.info(f"🧠 Memory: {event.memory_type}")

subscribe(EventType.MEMORY_CREATED.value, on_memory_created)

async def on_trust_increased(event: BaseEvent) -> None:
    if not isinstance(event, TrustEvent): return
    logger.info(f"💕 Trust: {event.old_bond:.0f}% → {event.new_bond:.0f}%")

subscribe(EventType.TRUST_INCREASED.value, on_trust_increased)

async def on_goal_completed(event: BaseEvent) -> None:
    if not isinstance(event, GoalEvent): return
    logger.info(f"🏆 Goal: {event.title}")

subscribe(EventType.GOAL_COMPLETED.value, on_goal_completed)

async def on_attachment_detected(event: BaseEvent) -> None:
    if not isinstance(event, AttachmentEvent): return
    logger.info(f"🔍 Attachment: {event.style}")

subscribe(EventType.ATTACHMENT_DETECTED.value, on_attachment_detected)

async def on_reflection_completed(event: BaseEvent) -> None:
    if not isinstance(event, ReflectionEvent): return
    logger.info(f"💭 Reflection: {event.summary[:80]}...")

subscribe(EventType.REFLECTION_COMPLETED.value, on_reflection_completed)

async def on_journey_phase_changed(event: BaseEvent) -> None:
    if event.type.value != "journey_phase_changed": return
    logger.info(f"🗺️ Journey phase: {event.user_id}")

subscribe("journey_phase_changed", on_journey_phase_changed)

async def on_identity_evolved(event: BaseEvent) -> None:
    if event.type.value != "identity_evolved": return
    logger.info(f"🎭 Identity evolved: {event.user_id}")

subscribe("identity_evolved", on_identity_evolved)

logger.info("✅ All event handlers registered (with Telegram proactive)")
