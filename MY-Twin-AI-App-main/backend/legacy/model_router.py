"""
MyTwin – Intelligent Model Orchestrator v2.5 (True Load Balancing)
- يوزع الطلبات بذكاء مع تجنب المزودين الفاشلين
- توزيع عشوائي 60/40 للمهام العامة لتخفيف الضغط
- يتكامل مع multi_ai.py الذي يدعم 2 API Keys لكل مزود
"""
import logging
import random
import time
from typing import Optional, List, Dict

logger = logging.getLogger("model_router")

class ModelRouter:
    # تتبع فشل المزودين لتجنبهم مؤقتاً
    _provider_failures: Dict[str, float] = {}
    _cooldown_seconds = 30  # ثواني التبريد

    TASK_TO_PROVIDERS = {
        "emotional": ["gemini", "groq"],
        "deep_reasoning": ["openrouter", "groq"],
        "reasoning": ["openrouter", "groq"],
        "coding": ["groq", "gemini"],
        "search": ["groq", "openrouter"],
        "agent": ["groq", "openrouter"],
        "general": ["groq", "gemini"],
        "coaching": ["gemini", "groq"],
        "dream": ["gemini"],
        "quick_reply": ["groq", "gemini"],
        "translation": ["groq", "gemini"],
        "summarization": ["groq", "openrouter"],
    }

    EMOTION_PROVIDERS = {
        "sadness": ["gemini"],
        "fear": ["gemini"],
        "anger": ["gemini", "groq"],
        "joy": ["gemini", "openrouter"],
        "love": ["gemini"],
        "support": ["gemini"],
        "anxiety": ["gemini"],
    }

    @classmethod
    def _is_cooling_down(cls, provider: str) -> bool:
        """هل المزود في فترة تبريد؟"""
        if provider in cls._provider_failures:
            if time.time() - cls._provider_failures[provider] < cls._cooldown_seconds:
                return True
            else:
                del cls._provider_failures[provider]
        return False

    @classmethod
    def _mark_failed(cls, provider: str):
        """تسجيل فشل مزود"""
        cls._provider_failures[provider] = time.time()
        logger.warning(f"⚠️ تم تعليم {provider} كفاشل مؤقتاً لمدة {cls._cooldown_seconds}s")

    @classmethod
    def _mark_success(cls, provider: str):
        """إزالة من قائمة الفشل عند النجاح"""
        cls._provider_failures.pop(provider, None)

    @classmethod
    def get_preferred_providers(cls, task_type: str, emotion_primary: Optional[str] = None) -> List[str]:
        """يختار قائمة المزودين مع تجنب الفاشلين وتوزيع عشوائي ذكي"""
        # العاطفة القوية تطغى
        if emotion_primary and emotion_primary in cls.EMOTION_PROVIDERS:
            candidates = cls.EMOTION_PROVIDERS[emotion_primary][:]  # نسخة
        else:
            candidates = cls.TASK_TO_PROVIDERS.get(task_type, ["groq", "gemini"])[:]

        # إزالة المزودين الفاشلين
        healthy = [p for p in candidates if not cls._is_cooling_down(p)]

        # إذا الكل فاشل، نعيد القائمة الأصلية (مضطرين نحاول)
        if not healthy:
            healthy = candidates
            logger.warning("⚠️ جميع المزودين في تبريد، سيتم إعادة المحاولة")

        # توزيع عشوائي للمهام العامة (60% Groq, 40% Gemini)
        if task_type in ("general", "quick_reply") and "groq" in healthy and "gemini" in healthy:
            if random.random() < 0.6:
                healthy = ["groq", "gemini"]
            else:
                healthy = ["gemini", "groq"]

        logger.info(f"🧠 توجيه '{task_type}' (عاطفة: {emotion_primary}) → {healthy}")
        return healthy

    @classmethod
    async def get_best_reply(cls, prompt: str, task_type: str, multi_client,
                             emotion_primary: Optional[str] = None):
        """
        ينسق مع multi_client للحصول على أفضل رد مع تتبع الفشل.
        يُرجع (reply_text, provider_name).
        """
        preferred = cls.get_preferred_providers(task_type, emotion_primary)

        # محاولة كل مزود في القائمة المفضلة
        for provider in preferred:
            try:
                text, provider_name = await multi_client.get_best(
                    prompt, preferred_providers=[provider], task=task_type
                )
                cls._mark_success(provider)
                return text, provider_name
            except Exception as e:
                logger.warning(f"❌ {provider} فشل: {e}")
                cls._mark_failed(provider)
                continue

        # Fallback نهائي: أي مزود متاح
        try:
            text, provider_name = await multi_client.get_best(prompt, task=task_type)
            return text, f"{provider_name}(fallback)"
        except Exception as e:
            logger.error(f"❌ جميع المزودين فشلوا: {e}")
            raise


model_router = ModelRouter()
print("✅ Model Orchestrator v2.5 (True Load Balancing) initialized")
