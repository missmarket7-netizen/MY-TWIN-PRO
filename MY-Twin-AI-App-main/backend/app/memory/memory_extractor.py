"""Memory Extractor – summarization and entity extraction."""
import logging, asyncio
from typing import List, Dict, Optional

logger = logging.getLogger("memory_extractor")

_counter: Dict[str, int] = {}
SUMMARIZE_EVERY = 50


async def increment_counter(user_id: str) -> None:
    _counter[user_id] = _counter.get(user_id, 0) + 1


async def should_summarize(user_id: str) -> bool:
    return _counter.get(user_id, 0) >= SUMMARIZE_EVERY


async def reset_counter(user_id: str) -> None:
    _counter[user_id] = 0


async def generate_summary(messages: List[Dict[str, str]], twin_name: str = "توأمك") -> Optional[str]:
    """Generate a 2‑3 sentence summary using Gemini."""
    if not messages or len(messages) < 10:
        return None
    text = "\n".join(
        f"{'مستخدم' if m.get('role') == 'user' else 'توأم'}: {m.get('content', '')[:300]}"
        for m in messages[-SUMMARIZE_EVERY:]
    )
    try:
        from app.infrastructure.ai.gemini_client import generate_stream
        prompt = f"""لخص هذه المحادثة في 2-3 جمل عربية:
{text[:3000]}
الملخص:"""
        summary = ""
        async for chunk in generate_stream("", prompt):
            summary += chunk
        return summary.strip() if len(summary) > 10 else None
    except Exception as e:
        logger.warning(f"Summary generation failed: {e}")
        return None


async def extract_entities(text: str) -> List[str]:
    """Simple keyword entity extraction."""
    entities = set()
    for word in text.split():
        if len(word) > 3 and word.isalpha():
            entities.add(word)
    return list(entities)[:10]
