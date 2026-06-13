"""
MyTwin – Agent Loop v2.0 (Multi-Tool Chain)
- ينفذ خطة من Reasoning Engine بعدة خطوات (steps)
- يدعم سلاسل أدوات: Tool → Observe → Next Tool → ...
- يدمج نتائج جميع الأدوات في الرد النهائي
- max_iterations للتحكم في عدد الدورات
"""
import logging
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
        twin_brain_instance=None,
        context_summary: str = "",
        lang: str = "ar"
    ) -> Dict[str, Any]:
        """
        تنفيذ خطة الـ Agent بعدة خطوات.
        """
        iteration = 0
        tool_results = []
        final_response = None
        steps = plan.get("steps", [])
        primary_tool = plan.get("primary_tool")
        
        # إذا لم تكن هناك خطوات، ننشئ خطوة واحدة من الأداة الأساسية
        if not steps and primary_tool:
            steps = [f"Execute {primary_tool}"]

        while iteration < self.max_iterations:
            iteration += 1
            
            # 1. تحديد الأداة الحالية
            current_tool = None
            if iteration <= len(steps):
                # استخدام الأداة من الخطة إذا كانت متاحة
                if iteration == 1 and primary_tool:
                    current_tool = primary_tool
                else:
                    # البحث عن أداة في الخطوة الحالية
                    step_text = steps[iteration - 1] if iteration - 1 < len(steps) else ""
                    current_tool = self._extract_tool_from_step(step_text)
            
            # إذا لم نجد أداة، نتوقف
            if not current_tool:
                break

            # 2. تنفيذ الأداة
            try:
                from reasoning_engine import ToolRegistry
                tool_func = ToolRegistry.get_tool(current_tool)
                if tool_func:
                    logger.info(f"🔧 Agent Loop: تنفيذ {current_tool} (دورة {iteration})")
                    result = await tool_func(user_id=user_id, query=message)
                    if result:
                        tool_results.append({
                            "tool": current_tool,
                            "result": result,
                            "iteration": iteration
                        })
                        
                        # 3. مراقبة النتيجة (Observation)
                        if plan.get("replan_if"):
                            if plan["replan_if"] in result or "خطأ" in result:
                                logger.info("🔄 إعادة التخطيط بناءً على نتيجة الأداة")
                                if twin_brain_instance:
                                    from reasoning_engine import reasoning_engine
                                    new_plan = await reasoning_engine.create_execution_plan(
                                        message=message,
                                        emotion=emotion,
                                        context_summary=f"{context_summary}\nنتيجة الأداة السابقة: {result}"
                                    )
                                    plan = new_plan
                                    steps = plan.get("steps", [])
                                    continue  # دورة جديدة
                else:
                    logger.warning(f"الأداة {current_tool} غير موجودة في ToolRegistry")
            except Exception as e:
                logger.error(f"فشل تنفيذ الأداة {current_tool}: {e}")

            # 4. التحقق من الحاجة لأداة أخرى
            if iteration >= len(steps):
                # جميع الخطوات نفذت
                break

        # 5. توليد الرد النهائي مع نتائج الأدوات
        if twin_brain_instance and tool_results:
            try:
                # دمج نتائج الأدوات في سياق الرد
                tools_context = "\n".join([f"{t['tool']}: {t['result']}" for t in tool_results])
                response = await twin_brain_instance.respond(
                    message=message,
                    user_id=user_id,
                    emotion=emotion,
                    tool_results=[t["result"] for t in tool_results]
                )
                if response:
                    response["tool_results"] = tool_results
                    response["provider"] = "agent_loop"
                    final_response = response
            except Exception as e:
                logger.error(f"فشل توليد الرد النهائي: {e}")

        # إذا لم نستطع توليد رد، نرجع نتائج الأدوات مباشرة
        if not final_response and tool_results:
            combined = "\n\n".join([t["result"] for t in tool_results])
            final_response = {
                "reply": combined,
                "provider": "agent_loop",
                "tool_results": tool_results
            }

        if not final_response:
            final_response = {
                "reply": "عذراً، لم أتمكن من معالجة طلبك. حاول مرة أخرى.",
                "provider": "agent_loop"
            }

        return final_response

    def _extract_tool_from_step(self, step_text: str) -> Optional[str]:
        """استخراج اسم الأداة من نص الخطوة."""
        from reasoning_engine import ToolRegistry
        available = ToolRegistry.list_tools()
        for tool in available:
            if tool in step_text:
                return tool
        return None


agent_loop = AgentLoop()
print("✅ Agent Loop v2.0 (Multi-Tool Chain)")
