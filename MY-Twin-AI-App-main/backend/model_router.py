"""
MyTwin – Intelligent Model Router v1.5 (Deep Integration)
- يختار أفضل نموذج AI بناءً على نوع المهمة وعاطفة المستخدم
- Emotional → Gemini (عاطفي)
- Reasoning → Llama 4 (OpenRouter) (تحليل عميق)
- Search/Tools → Groq (سريع ورخيص)
- عام → Gemini Flash (افتراضي)
- متكامل مع multi_ai و twin_brain
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("model_router")

class ModelRouter:
    # خريطة المهام إلى النماذج
    TASK_TO_MODEL = {
        "emotional": "gemini",
        "deep_reasoning": "openrouter",
        "reasoning": "openrouter",
        "coding": "groq",
        "search": "groq",
        "agent": "groq",
        "general": "gemini",
        "coaching": "gemini",
        "dream": "gemini",
    }

    # تأثير العاطفة على اختيار النموذج
    EMOTION_MODEL_OVERRIDE = {
        "sadness": "gemini",      # حزين → Gemini (أكثر تعاطفاً)
        "fear": "gemini",         # خائف → Gemini
        "anger": "groq",          # غاضب → Groq (سريع ومباشر)
        "joy": "openrouter",      # سعيد → OpenRouter (إبداعي)
        "love": "gemini",         # حب → Gemini
    }

    @classmethod
    def get_model_for_task(cls, task_type: str, emotion_primary: Optional[str] = None) -> str:
        """
        اختيار النموذج بناءً على المهمة والعاطفة.
        """
        # إذا كانت العاطفة قوية، قد تطغى على اختيار المهمة
        if emotion_primary and emotion_primary in cls.EMOTION_MODEL_OVERRIDE:
            if emotion_primary in ["sadness", "fear", "love"]:
                return "gemini"
            elif emotion_primary == "anger":
                return "groq"

        return cls.TASK_TO_MODEL.get(task_type, "gemini")

    @classmethod
    async def get_best_reply(cls, prompt: str, task_type: str, multi_client,
                             emotion_primary: Optional[str] = None) -> str:
        """
        توجيه الطلب إلى النموذج المناسب.
        """
        model_choice = cls.get_model_for_task(task_type, emotion_primary)
        logger.info(f"🧠 Model Router: task={task_type}, emotion={emotion_primary} → {model_choice}")

        # استدعاء النموذج المناسب عبر multi_client
        if model_choice == "gemini":
            if hasattr(multi_client, '_try_gemini'):
                return await multi_client._try_gemini(prompt)
        elif model_choice == "openrouter":
            if hasattr(multi_client, '_try_openrouter'):
                return await multi_client._try_openrouter(prompt)
        elif model_choice == "groq":
            if hasattr(multi_client, '_try_groq'):
                return await multi_client._try_groq(prompt)

        # fallback: استخدام الطريقة الافتراضية
        return await multi_client.get_best_reply(prompt, task=task_type)


# نسخة عالمية
model_router = ModelRouter()
print("✅ Model Router v1.5 initialized")
