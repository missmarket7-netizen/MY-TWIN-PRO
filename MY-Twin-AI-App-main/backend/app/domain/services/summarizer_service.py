"""
Summarizer Service – compresses conversations into permanent memories.
Extracted from memory_summarizer.py, rebuilt for hexagonal architecture.
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("summarizer_service")

# Counter per user (in-memory; migrate to Redis for production)
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
    """
    Summarize recent conversation and store as a permanent memory.
    Uses Gemini for smart summarization; falls back to keyword extraction.
    """
    if not messages or len(messages) < 10:
        return None

    recent = messages[-MAX_MESSAGES_BEFORE_SUMMARY:]
    conversation_text = "\n".join(
        f"{'مستخدم' if m.get('role') == 'user' else 'توأم'}: {m.get('content', '')[:300]}"
        for m in recent
    )

    # Try Gemini summarization
    summary = await _generate_summary(conversation_text, twin_name)

    if not summary:
        summary = _fallback_summary(recent)

    # Store via memory_repo
    try:
        from app.infrastructure.database.memory_repo import store_memory
        await store_memory(
            user_id=user_id,
            content=f"[ملخص] {summary}",
            memory_type="conversation_summary",
            importance=0.8,
        )
        logger.info(f"✅ Memory summarized and stored for {user_id}")
    except Exception as e:
        logger.warning(f"Failed to store summary: {e}")

    await reset_counter(user_id)
    return summary


async def _generate_summary(text: str, twin_name: str) -> Optional[str]:
    """Use Gemini to generate a smart summary."""
    try:
        from app.infrastructure.ai.gemini_client import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            return None

        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""أنت {twin_name}، التوأم الرقمي. لخص هذه المحادثة في 2-3 جمل بالعامية المصرية.
ركز على: المواضيع الرئيسية، المشاعر السائدة، أي قرارات أو أهداف ذُكرت.
لا تضف شيئاً من عندك.

المحادثة:
{text[:3000]}

الملخص:"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if response.text and len(response.text) > 10:
            return response.text.strip()
    except Exception as e:
        logger.warning(f"AI summarization failed: {e}")
    return None


def _fallback_summary(messages: List[Dict[str, str]]) -> str:
    """Extract keywords as fallback summary."""
    topics = set()
    for m in messages:
        if m.get("role") == "user":
            words = m.get("content", "").split()
            topics.update(w for w in words if len(w) > 3)
    return f"محادثة تناولت مواضيع: {', '.join(list(topics)[:5])}"
