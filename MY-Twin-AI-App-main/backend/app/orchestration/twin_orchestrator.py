"""Twin Orchestrator v13.0.0 – with Semantic Memory."""
import time, logging, asyncio, random, traceback
from typing import Dict, Any, Optional

logger = logging.getLogger("twin_orchestrator")

try:
    from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
    from app.infrastructure.ai.council import council
    from app.infrastructure.ai.self_critic import self_critic
    from app.domain.services.safety_service import check_safety, sanitize_input
    from app.twin_state.relationship_service import detect_intent
    from app.repositories.profile_repository import get_profile
    from app.memory.memory_retriever import retrieve_and_summarize
    from app.memory.memory_service import save as save_memory
    from app.infrastructure.cache.cache_service import get_cached_response, set_cached_response
except Exception as e:
    logger.error(f"Import error: {e}")

FALLBACK_REPLIES = [
    "أنا هنا معك 💜 كيف يمكنني مساعدتك؟",
    "هل هناك شيء يشغل بالك تريد التحدث عنه؟",
    "أنا سعيد لأنك هنا! ماذا تريد أن تفعل اليوم؟",
    "دعني أساعدك. ما الذي تبحث عنه؟",
    "أهلاً بك! أنا توأمك الرقمي، في خدمتك دائمًا 🌸",
]

async def orchestrate(
    user_id: str, message: str, history: list = None,
    lang: str = "ar", calm_mode: bool = False, voice_enabled: bool = False,
) -> str:
    start_time = time.time()
    logger.info(f"🎯 Orchestrate: user={user_id}, msg={message[:50]}...")

    # 1. Safety
    safety = check_safety(message)
    if not safety.get("safe") and safety.get("severity") == "critical":
        return safety.get("helpline", "أنا هنا لدعمك 💜")
    clean = sanitize_input(message)

    # 2. Cache check
    cached = get_cached_response(clean, "MyTwin", lang)
    if cached:
        logger.info("⚡ Cache hit")
        return cached

    # 3. Intent
    intent, _ = detect_intent(clean, lang)
    logger.info(f"   intent={intent}")

    # 4. Memory retrieval
    memory_context = ""
    try:
        memories = await retrieve_and_summarize([], user_id, top_k=3)
        if memories and memories.get("memories"):
            mem_lines = [f"- {m.content[:200]}" for m in memories["memories"][:3] if hasattr(m, 'content')]
            memory_context = "<MEMORIES>\n" + "\n".join(mem_lines) + "\n</MEMORIES>"
            logger.info(f"🧠 {len(memories['memories'])} memories retrieved")
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")

    # 5. Load profile
    profile = None
    try: profile = await get_profile(user_id)
    except: pass

    # 6. Try AI
    if provider_router and council:
        try:
            full_prompt = f"{memory_context}\nالمستخدم: {clean}\nاللغة: {lang}\nالنية: {intent}\nأجب بلطف وإيجاز."
            response, provider_name = await council.get_best_reply(
                prompt=full_prompt, task=intent, emotion="neutral",
                message=clean, intent=intent,
            )
            if response and len(response.strip()) > 5:
                if self_critic:
                    response = await self_critic.evaluate(response)
                set_cached_response(clean, "MyTwin", lang, response, ttl=300)
                logger.info(f"✅ AI reply: {len(response)} chars via {provider_name}")
                return response
        except AIUnavailable:
            logger.warning("⚠️ AI unavailable, using fallback")
        except Exception as e:
            logger.error(f"❌ AI error: {traceback.format_exc()}")

    # 7. Fallback
    fallback = random.choice(FALLBACK_REPLIES)
    logger.info(f"🔄 Fallback: {fallback}")
    return fallback
