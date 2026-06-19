"""Twin Orchestrator v12.8.0 – with Fallback & Detailed Logging."""
import time, logging, asyncio, traceback
from typing import Dict, Any, Optional

logger = logging.getLogger("twin_orchestrator")

# استيرادات آمنة مع احتياط
try:
    from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
except:
    provider_router = None
    class AIUnavailable(Exception): pass

try:
    from app.infrastructure.ai.council import council
except:
    council = None

try:
    from app.infrastructure.ai.self_critic import self_critic
except:
    self_critic = None

try:
    from app.domain.services.safety_service import check_safety, sanitize_input
except:
    def check_safety(t): return {"safe": True, "severity": "low"}
    def sanitize_input(t): return t

try:
    from app.twin_state.relationship_service import detect_intent
except:
    def detect_intent(t, l): return "general", 1.0

try:
    from app.repositories.profile_repository import get_profile
except:
    async def get_profile(uid): return None

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

    # 2. Intent
    intent, _ = detect_intent(clean, lang)
    logger.info(f"   intent={intent}")

    # 3. Load profile
    profile = None
    try: profile = await get_profile(user_id)
    except: pass

    # 4. Try AI
    if provider_router and council:
        try:
            prompt = f"المستخدم: {clean}\nاللغة: {lang}\nالنية: {intent}\nأجب بلطف وإيجاز."
            response, provider_name = await council.get_best_reply(
                prompt=prompt, task=intent, emotion="neutral",
                message=clean, intent=intent,
            )
            if response and len(response.strip()) > 5:
                if self_critic:
                    response = await self_critic.evaluate(response)
                logger.info(f"✅ AI reply: {len(response)} chars via {provider_name}")
                return response
        except AIUnavailable:
            logger.warning("⚠️  AI unavailable, using fallback")
        except Exception as e:
            logger.error(f"❌ AI error: {traceback.format_exc()}")

    # 5. Fallback
    import random
    fallback = random.choice(FALLBACK_REPLIES)
    logger.info(f"🔄 Fallback: {fallback}")
    return fallback
