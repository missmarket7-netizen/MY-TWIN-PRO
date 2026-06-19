"""Context Service – builds full context for chat."""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("context_service")

try:
    from app.context_manager import context_manager
except ImportError:
    context_manager = None

async def build_context(user_id: str, message: str, emotion: Optional[Dict] = None, history: Optional[List[Dict]] = None, lang: str = "ar", tier: str = "free", intent: str = "general") -> Dict[str, Any]:
    if not context_manager:
        return {"memories": [], "relationship": {}, "consciousness": {}, "attachment": {}}
    try:
        return await context_manager.build_context(
            user_id=user_id, message=message, emotion=emotion or {},
            history=history, lang=lang, tier=tier, intent=intent
        )
    except Exception as e:
        logger.warning(f"Context build failed: {e}")
        return {}

def format_context_for_prompt(context: Dict[str, Any], lang: str = "ar") -> str:
    if not context_manager:
        return ""
    return context_manager.format_context_for_prompt(context, lang)
