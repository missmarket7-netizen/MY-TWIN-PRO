"""
MyTwin – Intelligent Model Orchestrator v2.1 (Cost & Load Balanced)
- يوزع الطلبات على Groq/OpenRouter/Gemini حسب المهمة والعاطفة
- يُفضل Groq للمهام البسيطة (مجاني، سريع) لتخفيف الضغط على Gemini
- يُفضل Gemini للعاطفة واللغة العربية (متعاطف)
- يُفضل OpenRouter للمهام التحليلية المعقدة
"""
import logging
import random
from typing import Optional, List

logger = logging.getLogger("model_router")

class ModelRouter:
    # الأولويات حسب المهمة (الأول = الأكثر تفضيلاً)
    TASK_TO_PROVIDERS = {
        "emotional": ["gemini", "groq"],
        "deep_reasoning": ["openrouter", "groq"],
        "reasoning": ["openrouter", "groq"],
        "coding": ["groq", "gemini"],
        "search": ["groq", "openrouter"],
        "agent": ["groq", "openrouter"],
        "general": ["groq", "gemini"],          # ⭐ Groq أولاً لتخفيف الحمل عن Gemini
        "coaching": ["gemini", "groq"],
        "dream": ["gemini"],
        "quick_reply": ["groq", "gemini"],       # ردود سريعة
        "translation": ["groq", "gemini"],
        "summarization": ["groq", "openrouter"],
    }

    # تأثير العاطفة يطغى على اختيار المهمة
    EMOTION_PROVIDERS = {
        "sadness": ["gemini"],
        "fear": ["gemini"],
        "anger": ["gemini", "groq"],   # Gemini أكثر تعاطفاً حتى مع الغضب
        "joy": ["gemini", "openrouter"],
        "love": ["gemini"],
        "support": ["gemini"],
        "anxiety": ["gemini"],
    }

    @classmethod
    def get_preferred_providers(cls, task_type: str, emotion_primary: Optional[str] = None) -> List[str]:
        """يختار قائمة المزودين المفضلين حسب المهمة والعاطفة."""
        # العاطفة القوية تطغى
        if emotion_primary and emotion_primary in cls.EMOTION_PROVIDERS:
            return cls.EMOTION_PROVIDERS[emotion_primary]

        return cls.TASK_TO_PROVIDERS.get(task_type, ["groq", "gemini"])

    @classmethod
    async def get_best_reply(cls, prompt: str, task_type: str, multi_client,
                             emotion_primary: Optional[str] = None):
        """
        ينسق مع multi_client للحصول على أفضل رد بأقل تكلفة.
        يُرجع (reply_text, provider_name).
        """
        preferred = cls.get_preferred_providers(task_type, emotion_primary)
        logger.info(f"🧠 توجيه المهمة '{task_type}' (عاطفة: {emotion_primary}) → {preferred}")
        try:
            text, provider = await multi_client.get_best(prompt, preferred_providers=preferred, task=task_type)
            return text, provider
        except Exception:
            # Fallback: أي مزود متاح
            text, provider = await multi_client.get_best(prompt, task=task_type)
            return text, f"{provider}(fallback)"


model_router = ModelRouter()
print("✅ Model Orchestrator v2.1 (Cost/Load Balanced) initialized")
