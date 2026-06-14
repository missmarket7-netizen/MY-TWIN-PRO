import logging
from typing import Optional

logger = logging.getLogger("model_router")

class ModelRouter:
    TASK_TO_PROVIDERS = {
        "emotional": ["gemini", "openrouter"],
        "deep_reasoning": ["openrouter", "groq"],
        "reasoning": ["openrouter", "groq"],
        "coding": ["groq", "gemini"],
        "search": ["groq", "openrouter"],
        "agent": ["groq", "openrouter"],
        "general": ["gemini", "groq"],
        "coaching": ["gemini", "openrouter"],
        "dream": ["gemini"],
    }
    EMOTION_PROVIDERS = {
        "sadness": ["gemini"], "fear": ["gemini"],
        "anger": ["groq"], "joy": ["openrouter", "gemini"],
        "love": ["gemini"],
    }

    @classmethod
    def get_preferred_providers(cls, task_type: str, emotion_primary: Optional[str] = None):
        if emotion_primary and emotion_primary in cls.EMOTION_PROVIDERS:
            return cls.EMOTION_PROVIDERS[emotion_primary]
        return cls.TASK_TO_PROVIDERS.get(task_type, ["gemini", "groq"])

    @classmethod
    async def get_best_reply(cls, prompt: str, task_type: str, multi_client, emotion_primary: Optional[str] = None):
        preferred = cls.get_preferred_providers(task_type, emotion_primary)
        logger.info(f"Model Router -> {preferred}")
        try:
            text, provider = await multi_client.get_best(prompt, preferred_providers=preferred, task=task_type)
            return text, provider
        except Exception:
            text, provider = await multi_client.get_best(prompt, task=task_type)
            return text, f"{provider}(fallback)"

model_router = ModelRouter()
print("✅ Model Orchestrator v2.0 ready")
