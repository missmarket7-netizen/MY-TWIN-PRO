"""Agent Loop – Complete with planning, execution, and budget management."""
import logging, time
from typing import Dict, Any, Optional, List
from app.infrastructure.ai.provider_router import provider_router, AIUnavailable

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
        """Execute agent plan with tool routing and budget management."""
        from app.features.tool_registry import ToolRegistry
        from app.features.agent_budget import agent_budget
        from app.features.tool_executor import tool_executor

        tool_results = []
        calls_made = 0
        cost_so_far = 0.0
        start_time = time.time()
        tier = "free"
        scratchpad = {"entries": [], "used_tools": set()}

        def add_thought(thought: str):
            scratchpad["entries"].append({"type": "thought", "content": thought})

        def add_action(tool_name: str):
            scratchpad["entries"].append({"type": "action", "content": tool_name})
            scratchpad["used_tools"].add(tool_name)

        def add_observation(result: str):
            scratchpad["entries"].append({"type": "observation", "content": result[:300]})

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            time_elapsed = (time.time() - start_time) * 1000

            # Get available tools
            available = [t for t in ToolRegistry.list_tools() if t not in scratchpad["used_tools"]]
            if not available:
                add_thought("No more tools available")
                break

            # Decide next action using LLM
            next_tool = await self._decide_next_action(
                message, scratchpad, available, emotion.get("primary", "neutral")
            )
            
            if not next_tool or next_tool == "done":
                add_thought("Task completed")
                break

            if next_tool in scratchpad["used_tools"]:
                add_thought(f"Tool {next_tool} already used, skipping")
                continue

            if not agent_budget.can_execute(next_tool, calls_made, cost_so_far, time_elapsed, tier):
                add_thought("Budget exceeded, stopping")
                break

            add_action(next_tool)
            calls_made += 1
            cost_so_far += agent_budget.get_tool_cost(next_tool)

            result = await tool_executor.execute(
                tool_name=next_tool,
                message=message,
                user_id=user_id,
                tier=tier,
            )

            if result:
                add_observation(result)
                tool_results.append({"tool": next_tool, "result": result, "iteration": iteration})
            else:
                add_observation(f"Tool {next_tool} returned no result")

        # Synthesize final reply
        if tool_results:
            final_reply = self._synthesize_results(tool_results, message, lang)
            return {"reply": final_reply, "provider": "agent_loop", "tool_results": tool_results}

        return {"reply": "عذراً، لم أتمكن من معالجة طلبك.", "provider": "agent_loop", "tool_results": []}

    async def _decide_next_action(self, message: str, scratchpad: Dict, available: List[str], emotion: str) -> Optional[str]:
        """Use AI to decide the next best tool."""
        if not available:
            return None
        
        tools_list = ", ".join(available)
        context = "\n".join(
            f"{e['type']}: {e['content'][:200]}"
            for e in scratchpad["entries"][-5:]
        )
        
        prompt = f"""Context: {context}
Available tools: {tools_list}
Message: "{message}"
Emotion: {emotion}

Return ONLY the name of one tool to use next, or 'done' if finished."""
        
        try:
            reply, _ = await provider_router.route(prompt, task="quick_reply", tier="free")
            if reply:
                reply = reply.strip().lower()
                for tool in available:
                    if tool in reply:
                        return tool
                if "done" in reply:
                    return None
        except AIUnavailable:
            pass
        
        # Return first available as fallback
        return available[0] if available else None

    def _synthesize_results(self, tool_results: List[Dict], message: str, lang: str) -> str:
        """Combine tool results into a coherent response."""
        if not tool_results:
            return "لم أتمكن من الحصول على نتائج."
        
        if len(tool_results) == 1:
            return tool_results[0].get("result", "")
        
        parts = []
        for tr in tool_results:
            tool_name = tr.get("tool", "أداة")
            result = tr.get("result", "")
            parts.append(f"**{tool_name}**:\n{result}")
        
        return "\n\n".join(parts)


agent_loop = AgentLoop()
print("✅ Agent Loop v5.0 (Complete)")
