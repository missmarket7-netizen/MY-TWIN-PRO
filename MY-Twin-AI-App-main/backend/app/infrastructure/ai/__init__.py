"""
AI Infrastructure – مزودي ونماذج الذكاء الاصطناعي
====================================================
- provider_router: موازن ذكي متعدد المزودين
- provider_router_internal: موزع بين النموذج الداخلي والخارجي
- council: مجلس ذكي لتحسين الردود
- self_critic: مراقب جودة الردود
- internal_model_provider: النموذج الداخلي (LLaMA 3)
- embedding_client: توليد التضمينات
- dialect_service: كشف اللهجة وتوجيه الأسلوب
- prompt_templates: قوالب احتياطية
- gemini_client: عميل التدفق متعدد المزودين
"""
from .provider_router import (
    provider_router,
    AIUnavailable,
    APIKeyManager,
    MultiAIClient,
)
from .provider_router_internal import generate_with_fallback
from .council import council
from .self_critic import self_critic
from .internal_model_provider import internal_model
from .embedding_client import generate_embedding, generate_embeddings_batch
from .dialect_service import (
    get_dialect_for_user,
    get_dialect_prompt,
    get_dialect_profile,
    detect_and_store_dialect,
)
from .prompt_templates import get_system_prompt, get_feature_template
from .gemini_client import generate_stream

__all__ = [
    "provider_router",
    "AIUnavailable",
    "APIKeyManager",
    "MultiAIClient",
    "generate_with_fallback",
    "council",
    "self_critic",
    "internal_model",
    "generate_embedding",
    "generate_embeddings_batch",
    "get_dialect_for_user",
    "get_dialect_prompt",
    "get_dialect_profile",
    "detect_and_store_dialect",
    "get_system_prompt",
    "get_feature_template",
    "generate_stream",
]
