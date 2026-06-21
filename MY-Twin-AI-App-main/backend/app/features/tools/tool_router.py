"""Tool Router v4.0 – متوافق مع Unified Tool Registry."""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("tool_router")

class ToolRouter:
    def __init__(self):
        self.keyword_map = {
            "طقس": "get_weather", "weather": "get_weather",
            "أخبار": "get_news", "news": "get_news",
            "عملة": "get_currency", "currency": "get_currency",
            "بحث": "search_google", "search": "search_google",
            "ذاكرة": "reflections", "memory": "reflections",
            "هوية": "user_identity", "identity": "user_identity",
            "عاطفة": "emotional_state", "emotion": "emotional_state",
            "دراسة": "study", "study": "study",
            "مشروع": "business", "business": "business",
            "كود": "code", "code": "code",
            "حلم": "dream", "dream": "dream",
            "نصيحة": "recommendation", "advice": "recommendation",
        }

    async def route(self, message: str, user_id: str, tier: str = "free") -> Optional[str]:
        if not message: return None
        tool_name = self._detect(message)
        if not tool_name: return None
        
        from app.features.tools.tool_executor import tool_executor
        return await tool_executor.execute(tool_name, message, user_id, tier)

    def _detect(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        for keyword, tool_name in self.keyword_map.items():
            if keyword in msg_lower:
                return tool_name
        return None

tool_router = ToolRouter()
