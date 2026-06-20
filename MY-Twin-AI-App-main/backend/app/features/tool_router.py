"""Tool Router – Smart routing with caching and fallback."""
import logging, time
from typing import Optional, Dict, Any, List
from app.features.tool_executor import tool_executor
from app.features.tool_registry import ToolRegistry
from app.infrastructure.cache.cache_service import get as cache_get, set as cache_set

logger = logging.getLogger("tool_router")

class ToolRouter:
    def __init__(self):
        self.default_tools = {
            "طقس": "get_weather",
            "weather": "get_weather",
            "يوتيوب": "search_youtube", 
            "youtube": "search_youtube",
            "أخبار": "get_news",
            "news": "get_news",
            "عملة": "get_currency",
            "currency": "get_currency",
            "سبوتيفاي": "search_spotify",
            "spotify": "search_spotify",
            "بحث": "search_google",
            "search": "search_google",
            "موسيقى": "search_youtube",
            "music": "search_youtube",
            "فيديو": "search_youtube",
            "video": "search_youtube",
        }

    async def route(
        self,
        message: str,
        user_id: str,
        tier: str = "free",
        user_profile: Optional[Dict[str, Any]] = None,
        emotion: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Route message to appropriate tool with caching."""
        if not message:
            return None

        # Check cache first
        cache_key = f"tool:{user_id}:{message[:50]}"
        cached = cache_get(cache_key)
        if cached:
            logger.info(f"⚡ Tool cache hit for {user_id}")
            return cached

        # Detect tool from message
        tool_name = self._detect_tool(message)
        if not tool_name:
            return None

        # Check if tool is available for tier
        available = ToolRegistry.list_tools()
        if tool_name not in available:
            return None

        # Execute tool with timeout
        start = time.time()
        try:
            result = await tool_executor.execute(
                tool_name=tool_name,
                message=message,
                user_id=user_id,
                tier=tier,
                user_profile=user_profile,
            )
            
            if result:
                # Cache for 5 minutes
                cache_set(cache_key, result, 300)
                logger.info(f"✅ Tool {tool_name} executed in {(time.time() - start)*1000:.0f}ms")
                return result
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")

        return None

    def _detect_tool(self, message: str) -> Optional[str]:
        """Detect which tool to use based on message keywords."""
        msg_lower = message.lower()
        
        # Check keyword map
        for keyword, tool_name in self.default_tools.items():
            if keyword in msg_lower:
                return tool_name
        
        # Check tool descriptions
        for tool_name, desc in ToolRegistry.get_tool_descriptions().items():
            if any(word in msg_lower for word in desc.lower().split()):
                return tool_name
        
        return None

    async def route_multiple(
        self,
        message: str,
        user_id: str,
        tier: str = "free",
        user_profile: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Route to all relevant tools."""
        results = []
        available = ToolRegistry.list_tools()
        
        for tool_name in available:
            if self._is_tool_relevant(tool_name, message):
                result = await tool_executor.execute(
                    tool_name=tool_name,
                    message=message,
                    user_id=user_id,
                    tier=tier,
                    user_profile=user_profile,
                )
                if result:
                    results.append({"tool": tool_name, "result": result})
        
        return results

    def _is_tool_relevant(self, tool_name: str, message: str) -> bool:
        """Check if a tool is relevant for a message."""
        msg_lower = message.lower()
        desc = ToolRegistry.get_tool_descriptions().get(tool_name, "")
        return any(word in msg_lower for word in desc.lower().split())


tool_router = ToolRouter()
print("✅ Tool Router v3.0 (Complete)")
