"""Tool Executor – Dynamic execution with caching and metrics."""
import logging, time, inspect, asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.features.tool_registry import ToolRegistry
from app.infrastructure.cache.cache_service import get as cache_get, set as cache_set

logger = logging.getLogger("tool_executor")

# In-memory cache with TTL
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300  # 5 minutes

class ToolExecutor:
    async def execute(
        self,
        tool_name: str,
        message: str,
        user_id: str,
        tier: str = "free",
        user_profile: Optional[Dict] = None,
    ) -> Optional[str]:
        """Execute a tool with caching, error handling, and metrics."""
        tool_func = ToolRegistry.get_tool(tool_name)
        if not tool_func:
            logger.warning(f"Tool not found: {tool_name}")
            return None

        # Check cache
        cache_key = f"{user_id}:{tool_name}:{message[:50]}"
        if cache_key in _cache:
            cached = _cache[cache_key]
            if datetime.now() - cached["time"] < timedelta(seconds=CACHE_TTL):
                logger.info(f"⚡ Cache: {tool_name}")
                return cached["result"]

        # Build arguments
        args = self._build_args(tool_name, message, user_id, tier, user_profile)

        # Execute with timeout
        start = time.time()
        try:
            sig = inspect.signature(tool_func)
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name in args:
                    kwargs[param_name] = args[param_name]
                elif param.default is inspect.Parameter.empty:
                    pass
                elif param_name == "user_id":
                    kwargs[param_name] = user_id
                elif param_name == "query":
                    kwargs[param_name] = message
                elif param_name == "tier":
                    kwargs[param_name] = tier

            # Execute with timeout protection
            result = await asyncio.wait_for(tool_func(**kwargs), timeout=15.0)

            # Cache result
            _cache[cache_key] = {"result": result, "time": datetime.now()}

            latency = (time.time() - start) * 1000
            self._log_metric(user_id, tool_name, True, latency, message[:100], str(result)[:200])
            
            return result

        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Tool {tool_name} timed out")
            self._log_metric(user_id, tool_name, False, 15000, message[:100])
            return None
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            self._log_metric(user_id, tool_name, False, latency, message[:100], error=str(e)[:200])
            return None

    def _build_args(self, tool_name: str, message: str, user_id: str, tier: str, user_profile: Optional[Dict]) -> Dict[str, Any]:
        """Build arguments for tool execution."""
        args = {"user_id": user_id, "tier": tier}
        
        if tool_name == "get_weather":
            args["city"] = self._extract_city(message) or "Cairo"
        elif tool_name in ["search_youtube", "search_spotify", "search_google"]:
            args["query"] = self._extract_query(message)
            if tool_name == "search_youtube":
                args["lang"] = "ar"
        elif tool_name == "get_news":
            args["country"] = "sa"
        elif tool_name == "get_currency":
            args["base"] = "USD"
        elif tool_name in ["get_todoist_tasks", "get_calendar_events"]:
            if user_profile:
                args["token"] = user_profile.get("calendar_token", "")
        
        return args

    def _extract_city(self, text: str) -> Optional[str]:
        """Extract city name from text."""
        cities = ["القاهرة", "الإسكندرية", "الرياض", "جدة", "دبي", "أبوظبي", "Cairo", "Dubai", "Riyadh"]
        for city in cities:
            if city in text:
                return city
        return None

    def _extract_query(self, text: str) -> str:
        """Extract search query from text."""
        # Remove common prefixes
        prefixes = ["ابحث عن", "بحث عن", "search for", "play", "شغل"]
        query = text
        for prefix in prefixes:
            query = query.replace(prefix, "", 1)
        return query.strip() or text

    def _log_metric(self, user_id: str, tool_name: str, success: bool, latency_ms: float,
                    input_text: str = "", output_text: str = "", error: str = ""):
        """Log tool execution metric."""
        try:
            from app.features.agent_metrics import agent_metrics
            asyncio.create_task(agent_metrics.log_tool_execution(
                user_id=user_id, tool_name=tool_name, success=success,
                latency_ms=latency_ms, input_query=input_text,
                output_summary=output_text, error_message=error,
            ))
        except:
            pass


tool_executor = ToolExecutor()
print("✅ Tool Executor v3.0 (Complete)")
