"""Tool Executor v4.0 – متوافق مع Unified Tool Registry."""
import logging, time, asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger("tool_executor")

_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300

class ToolExecutor:
    async def execute(self, tool_name: str, message: str, user_id: str, tier: str = "free", user_profile: Optional[Dict] = None) -> Optional[str]:
        from app.features.tools.tool_registry import ToolRegistry
        
        tool_func = ToolRegistry.get_tool(tool_name)
        if not tool_func:
            logger.warning(f"Tool not found: {tool_name}")
            return None

        cache_key = f"{user_id}:{tool_name}:{message[:50]}"
        if cache_key in _cache:
            cached = _cache[cache_key]
            if datetime.now() - cached["time"] < timedelta(seconds=CACHE_TTL):
                return cached["result"]

        start = time.time()
        try:
            result = await asyncio.wait_for(tool_func(user_id, message), timeout=15.0)
            _cache[cache_key] = {"result": result, "time": datetime.now()}
            logger.info(f"✅ Tool {tool_name}: {(time.time()-start)*1000:.0f}ms")
            return result
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Tool {tool_name} timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            return None

tool_executor = ToolExecutor()
