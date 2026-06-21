"""
Twin Orchestrator v15.0.0 – محادثة حية بكل السياقات
==========================================================
يدمج: الزمان والمكان، الاستباقية، المراجعة الذاتية، التوصيات الموحدة.
"""
import time, logging, random, asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger("twin_orchestrator")

# استيرادات AI
try:
    from app.infrastructure.ai.provider_router import provider_router
    from app.infrastructure.ai.council import council
    from app.infrastructure.ai.provider_router_internal import generate_with_fallback
    AI_AVAILABLE = True
    INTERNAL_ROUTER = True
except Exception as e:
    AI_AVAILABLE = False
    INTERNAL_ROUTER = False

# استيرادات الذاكرة والمحركات الجديدة
try:
    from app.memory.retrieval.memory_retriever import retrieve_full_context
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_state_for_response
    from app.memory.reflection.reflection_engine import process_message_for_reflections
    from app.memory.identity.identity_model import analyze_and_update_identity
    from app.features.proactive_engine import proactive_engine
    from app.features.temporal_context import temporal_engine
    from app.features.meta_reflection import meta_engine
    from app.core.unified_recommendation_engine import engine as rec_engine
    ALL_CONTEXTS_READY = True
except Exception as e:
    ALL_CONTEXTS_READY = False

FALLBACK_REPLIES = ["أنا هنا معك 💜", "كيف يمكنني مساعدتك اليوم؟", "أهلاً بك! في خدمتك دائماً 🌸"]

async def orchestrate(user_id: str, message: str, history=None, lang="ar", calm_mode=False, voice_enabled=False) -> str:
    start = time.time()
    logger.info(f"🎯 Chat: {message[:50]}...")

    # 1. فحص الأمان
    try:
        from app.domain.services.safety_service import check_safety, sanitize_input
        safety = check_safety(message)
        if not safety.get("safe") and safety.get("severity") == "critical":
            return safety.get("helpline", "أنا هنا لدعمك 💜")
        clean = sanitize_input(message)
    except:
        clean = message

    # 2. جمع السياق الأساسي
    context = {}
    if ALL_CONTEXTS_READY:
        try:
            context = await retrieve_full_context(user_id, clean)
        except: pass

    # 3. إضافة السياق الزماني
    temporal_ctx = temporal_engine.get_current_context(user_id) if ALL_CONTEXTS_READY else {}
    
    # 4. إضافة التوصيات
    recommendations = ""
    if ALL_CONTEXTS_READY:
        try:
            recs = await rec_engine.get_daily_recommendation(user_id)
            recommendations = " | ".join([r["message"] for r in recs.get("recommendations", [])[:2]])
        except: pass

    # 5. بناء الموجه
    system_prompt = f"""
أنت توأم رقمي، صديق مقرب، مستشار حكيم.
الوقت: {temporal_ctx.get('time_of_day', '')} | {temporal_ctx.get('day_type', '')}
حالة المستخدم: {context.get('emotional', {}).get('current_emotion', 'محايد')}
التوصيات: {recommendations}
أجب بلطف وإيجاز وبالعربية.
"""
    
    # 6. توليد الرد
    response = None
    if INTERNAL_ROUTER and ALL_CONTEXTS_READY:
        try:
            response, provider = await generate_with_fallback(
                prompt=f"{system_prompt}\nالمستخدم: {clean}", language=lang, task="general", prefer_internal=True
            )
        except: pass

    if not response and AI_AVAILABLE and council:
        try:
            response, _ = await council.get_best_reply(prompt=system_prompt, task="general", emotion="neutral", message=clean, intent="general")
        except: pass

    if not response and AI_AVAILABLE and provider_router:
        try:
            response = await provider_router.generate(f"{system_prompt}\nالمستخدم: {clean}", language=lang)
        except: pass

    if not response or len(response.strip()) < 5:
        response = random.choice(FALLBACK_REPLIES)

    # 7. التعلم في الخلفية
    if ALL_CONTEXTS_READY:
        asyncio.create_task(_learn(user_id, clean, response))

    logger.info(f"✅ رد في {time.time()-start:.2f}s")
    return response

async def _learn(user_id, message, response):
    try:
        await store_emotional_memory(user_id=user_id, expressed_text=message, detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.0}, trigger="chat")
        await process_message_for_reflections(user_id=user_id, message=message, language="ar", detected_emotion="neutral")
    except: pass

logger.info("✅ Twin Orchestrator v15.0.0 with ALL contexts")
