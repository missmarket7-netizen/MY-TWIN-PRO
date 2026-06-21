"""Agent Loop v5.2 – متوافق مع Unified Tool Registry و async budget."""
import logging, time
from typing import Dict, Any, Optional, List

logger = logging.getLogger("agent_loop")

class AgentLoop:
    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations

    async def execute(
        self,
        plan: Dict[str, Any],
        user_id: str,
        message: str,
        emotion: Dict[str, Any],
        context_summary: str = "",
        lang: str = "ar",
    ) -> Dict[str, Any]:
        from app.features.tools.tool_registry import ToolRegistry
        from app.features.agent_budget import agent_budget
        from app.features.tools.tool_executor import tool_executor

        tool_results = []
        calls_made = 0
        cost_so_far = 0.0
        start_time = time.time()
        tier = "free"
        tools_used = set()

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            time_elapsed = (time.time() - start_time) * 1000

            all_tools = ToolRegistry.list_tools()
            available = [t for t in all_tools if t not in tools_used]
            if not available:
                break

            next_tool = await self._decide_next_action(message, available, emotion.get("primary", "neutral"))
            if not next_tool or next_tool == "done":
                break

            # ميزانية متزامنة (async)
            if not await agent_budget.can_execute(next_tool, calls_made, cost_so_far, time_elapsed, user_id, tier):
                break

            tools_used.add(next_tool)
            calls_made += 1
            cost_so_far += agent_budget.get_tool_cost(next_tool)

            result = await tool_executor.execute(
                tool_name=next_tool, message=message,
                user_id=user_id, tier=tier,
            )
            if result:
                tool_results.append({"tool": next_tool, "result": result, "iteration": iteration})

        if tool_results:
            return {"reply": self._synthesize_results(tool_results), "provider": "agent_loop", "tool_results": tool_results}
        return {"reply": "عذراً، لم أتمكن من معالجة طلبك.", "provider": "agent_loop", "tool_results": []}

    async def _decide_next_action(self, message: str, available: List[str], emotion: str) -> Optional[str]:
        if not available: return None
        try:
            from app.infrastructure.ai.provider_router import provider_router
            prompt = f"Available tools: {', '.join(available)}\nMessage: {message}\nEmotion: {emotion}\nReturn ONE tool name or 'done'."
            reply, _ = await provider_router.route(prompt, task="quick_reply", tier="free")
            if reply:
                reply = reply.strip().lower()
                for tool in available:
                    if tool in reply: return tool
                if "done" in reply: return None
        except: pass
        return available[0] if available else None

    def _synthesize_results(self, tool_results: List[Dict]) -> str:
        if len(tool_results) == 1: return tool_results[0].get("result", "")
        return "\n\n".join(f"**{tr['tool']}**:\n{tr['result']}" for tr in tool_results)

agent_loop = AgentLoop()
logger.info("✅ Agent Loop v5.2 ready")
