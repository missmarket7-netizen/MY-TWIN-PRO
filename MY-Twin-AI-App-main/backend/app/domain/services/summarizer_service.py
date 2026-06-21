"""
Summarizer Service v3.0 – متكامل مع TCMA Reflection Engine
=============================================================
- تلخيص المحادثات باستخدام TCMA أو AI
- تخزين الملخصات كاستنتاجات (Reflections)
- تكامل مع Memory Graph
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("summarizer_service")

_message_counters: Dict[str, int] = {}
MAX_MESSAGES_BEFORE_SUMMARY = 50

async def increment_counter(user_id: str) -> None:
    _message_counters[user_id] = _message_counters.get(user_id, 0) + 1

async def should_summarize(user_id: str) -> bool:
    return _message_counters.get(user_id, 0) >= MAX_MESSAGES_BEFORE_SUMMARY

async def reset_counter(user_id: str) -> None:
    _message_counters[user_id] = 0

async def summarize_and_store(
    user_id: str,
    messages: List[Dict[str, str]],
    twin_name: str = "توأمك",
) -> Optional[str]:
    """تلخيص المحادثة وتخزينها في TCMA"""
    if not messages or len(messages) < 10:
        return None

    recent = messages[-MAX_MESSAGES_BEFORE_SUMMARY:]
    conversation_text = "\n".join(
        f"{'مستخدم' if m.get('role') == 'user' else 'توأم'}: {m.get('content', '')[:300]}"
        for m in recent
    )

    # 1. محاولة التلخيص بـ AI
    summary = await _generate_summary(conversation_text, twin_name)
    if not summary:
        summary = _fallback_summary(recent)

    # 2. تخزين في TCMA (Reflection Engine)
    try:
        from app.memory.reflection.reflection_engine import store_reflection
        await store_reflection(
            user_id=user_id,
            insight_type="conversation_summary",
            insight_text=summary,
            confidence=0.8,
        )
        logger.info(f"✅ Conversation summarized for {user_id}")
    except Exception as e:
        logger.warning(f"Failed to store summary in TCMA: {e}")

    await reset_counter(user_id)
    return summary

async def _generate_summary(text: str, twin_name: str) -> Optional[str]:
    """تلخيص باستخدام الذكاء الاصطناعي"""
    try:
        from app.infrastructure.ai.provider_router import provider_router
        prompt = f"""لخص هذه المحادثة في 2-3 جمل بالعامية المصرية.
ركز على: المواضيع الرئيسية، المشاعر السائدة، أي قرارات.

المحادثة:
{text[:3000]}

الملخص:"""
        summary = await provider_router.generate(prompt, language="ar")
        if summary and len(summary) > 10:
            return summary.strip()
    except Exception as e:
        logger.warning(f"AI summarization failed: {e}")
    return None

def _fallback_summary(messages: List[Dict[str, str]]) -> str:
    """تلخيص احتياطي (كلمات مفتاحية)"""
    topics = set()
    for m in messages:
        if m.get("role") == "user":
            words = m.get("content", "").split()
            topics.update(w for w in words if len(w) > 3)
    return f"محادثة تناولت مواضيع: {', '.join(list(topics)[:5])}"

logger.info("✅ Summarizer Service v3.0 initialized (TCMA Integrated)")
