"""
Provider Router with Internal Model – موزع المزوّدين الذكي
============================================================
يختار بين النموذج الداخلي (MyTwin) والخارجي (Gemini/Groq).
يفضّل الداخلي للمحادثات العاطفية، والخارجي للمعرفة العامة.
"""
import logging
from typing import Optional, Tuple

logger = logging.getLogger("provider_router")

try:
    from app.infrastructure.ai.internal_model_provider import internal_model
    INTERNAL_AVAILABLE = True
except ImportError:
    INTERNAL_AVAILABLE = False

try:
    from app.infrastructure.ai.provider_router import provider_router as external_router
    EXTERNAL_AVAILABLE = True
except ImportError:
    EXTERNAL_AVAILABLE = False

async def generate_with_fallback(
    prompt: str,
    language: str = "ar",
    prefer_internal: bool = True,
    task: str = "general",
    emotion: str = "neutral",
) -> Tuple[str, str]:
    """
    يولّد رداً مع تدرج احتياطي ذكي:
    1. النموذج الداخلي (إذا كان متاحاً والمهمة مناسبة)
    2. النموذج الخارجي (Gemini/Groq)
    3. رد احتياطي
    """
    provider_used = "none"
    response = None

    # تحديد إن كان النموذج الداخلي مناسباً
    internal_suitable_tasks = ["general", "emotional", "personal", "chat"]
    use_internal = (
        INTERNAL_AVAILABLE and
        prefer_internal and
        task in internal_suitable_tasks and
        internal_model._loaded
    )

    # 1. محاولة النموذج الداخلي
    if use_internal:
        try:
            response = await internal_model.generate(prompt, max_tokens=200)
            if response and len(response.strip()) > 10:
                provider_used = "internal_mytwin"
                logger.info(f"✅ رد من النموذج الداخلي ({len(response)} حرف)")
                return response, provider_used
        except Exception as e:
            logger.warning(f"⚠️ فشل النموذج الداخلي: {e}")

    # 2. محاولة النموذج الخارجي
    if EXTERNAL_AVAILABLE and external_router:
        try:
            response = await external_router.generate(prompt, language=language)
            if response and len(response.strip()) > 5:
                provider_used = "external_api"
                logger.info(f"✅ رد من النموذج الخارجي ({len(response)} حرف)")
                return response, provider_used
        except Exception as e:
            logger.error(f"❌ فشل النموذج الخارجي: {e}")

    # 3. رد احتياطي
    fallback = "أنا هنا معك 💜" if language == "ar" else "I'm here with you 💜"
    return fallback, "fallback"

logger.info("✅ Provider Router with Internal Model جاهز")
