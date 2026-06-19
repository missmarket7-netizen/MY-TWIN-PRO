"""
Reasoning Service – Intent-driven execution planning.
Migrated from reasoning_engine.py with full logic preserved.
"""
import os, logging, json, re
from typing import Dict, Any, Optional, List, Tuple
from app.features.tool_registry import ToolRegistry

logger = logging.getLogger("reasoning_service")

VALID_INTENTS = {
    "general", "emotional", "coaching", "decision",
    "memory", "search", "weather", "music", "goal",
    "greeting", "gratitude", "goodbye", "news", "coding",
    "business", "career", "planning"
}

class ReasoningService:
    def __init__(self):
        self.client = None

    def _extract_json(self, text: str) -> Optional[Dict]:
        if not text: return None
        text = text.strip()
        if text.startswith("```json"): text = text[7:]
        elif text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        try: return json.loads(text.strip())
        except: pass
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            return json.loads(text[start:end])
        except: pass
        return None

    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(plan.get("subgoals"), list): plan["subgoals"] = []
        if not isinstance(plan.get("needs_tool"), bool): plan["needs_tool"] = False
        if not isinstance(plan.get("tool_confidence"), (int, float)): plan["tool_confidence"] = 0.5
        if not isinstance(plan.get("needs_memory"), bool): plan["needs_memory"] = False
        if not isinstance(plan.get("response_style"), str): plan["response_style"] = "conversational"
        if not isinstance(plan.get("goal"), str): plan["goal"] = "general_chat"
        if not isinstance(plan.get("intent"), str): plan["intent"] = "general"
        return plan

    def _should_use_llm_planner(self, message: str, emotion: Dict[str, Any]) -> bool:
        if len(message) < 15:
            return False
        if emotion.get("intensity", 0) < 0.4 and len(message) < 50:
            return False
        return True

    def _fast_plan(self, message: str, emotion: Dict[str, Any]) -> Dict[str, Any]:
        intent = "general"
        msg_lower = message.lower()
        
        patterns = {
            "weather": r"\b(طقس|الجو|الرياح|مطر|حرارة|شمس|سحاب|عاصفة|weather|rain|sunny|temperature)\b",
            "music": r"\b(أغنية|موسيقى|اسمع|شغل|باند|مطرب|song|music|playlist|spotify)\b",
            "news": r"\b(أخبار|حدث|حصل|عاجل|news|headlines|latest)\b",
            "currency": r"\b(عملة|دولار|ريال|سعر|صرف|currency|exchange|usd|sar)\b",
            "search": r"\b(بحث|search|google|معلومات عن|اعرف)\b",
            "goal": r"\b(هدف|أهداف|تقدم|خطة|plan|goal)\b",
            "memory": r"\b(ذكرت|قلت|اتذكر|remember|memory|سابق)\b",
            "emotional": r"\b(حزين|خايف|قلق|sad|worried|anxious|خوف|مكتئب)\b",
            "greeting": r"\b(مرحبا|اهلا|صباح الخير|مساء الخير|هاي|hello|hi)\b",
            "goodbye": r"\b(مع السلامة|باي|bye|goodbye)\b",
            "gratitude": r"\b(شكرا|تسلم|thanks|thank you)\b",
        }
        
        for intent_type, pattern in patterns.items():
            if re.search(pattern, msg_lower):
                intent = intent_type
                break

        tool_map = {
            "weather": "get_weather", "music": "search_spotify", "news": "get_news",
            "currency": "get_currency", "search": "search_google",
        }
        primary_tool = tool_map.get(intent) if intent in tool_map and tool_map[intent] in ToolRegistry.list_tools() else None
        
        return {
            "intent": intent,
            "goal": intent,
            "needs_tool": primary_tool is not None,
            "primary_tool": primary_tool,
            "all_tools": [primary_tool] if primary_tool else [],
            "steps": [],
            "response_style": "informative" if primary_tool else "conversational",
            "needs_memory": intent in ["memory", "emotional"],
            "tool_confidence": 0.8,
            "observation": "",
            "replan_if": "",
            "complexity": "simple",
            "urgency": "low",
            "risk_level": "low",
            "requires_empathy": intent == "emotional",
        }

    async def create_execution_plan(
        self, message: str, emotion: Dict[str, Any],
        user_id: Optional[str] = None, lang: str = "ar",
        context_summary: str = "", tier: str = "free"
    ) -> Dict[str, Any]:
        if not self._should_use_llm_planner(message, emotion):
            return self._fast_plan(message, emotion)

        # Try LLM planner if available
        if self.client:
            try:
                tools_desc = ToolRegistry.get_tool_descriptions(tier)
                tools_json = json.dumps(tools_desc, ensure_ascii=False)

                prompt = f"""أنت مخطط ذكي. حلل الموقف وخطط للخطوات.
                
السياق: {context_summary}
المشاعر: {emotion.get('primary', 'neutral')}
الأدوات: {tools_json}

أعد ONLY JSON:
{{
  "intent": "من {VALID_INTENTS}",
  "goal": "الهدف",
  "needs_tool": true/false,
  "primary_tool": "اسم الأداة أو null",
  "tool_confidence": 0.0-1.0,
  "needs_memory": true/false,
  "response_style": "conversational/informative/supportive/coaching",
  "complexity": "simple/medium/complex",
  "urgency": "low/medium/high",
  "risk_level": "low/medium/high",
  "requires_empathy": true/false
}}

الرسالة: "{message}"
JSON:"""

                raw_reply = await self.client.get_best_reply(prompt, task="deep_reasoning")
                plan = self._extract_json(raw_reply)
                if plan:
                    plan = self._validate_plan(plan)
                    primary_tool = plan.get("primary_tool")
                    available = ToolRegistry.list_tools()
                    
                    if primary_tool and primary_tool not in available:
                        plan["primary_tool"] = None
                        plan["needs_tool"] = False

                    return {
                        "intent": plan.get("intent", "general"),
                        "goal": plan.get("goal", "general_chat"),
                        "needs_tool": plan.get("needs_tool", False),
                        "primary_tool": plan.get("primary_tool"),
                        "tool_confidence": float(plan.get("tool_confidence", 0.5)),
                        "needs_memory": plan.get("needs_memory", False),
                        "response_style": plan.get("response_style", "conversational"),
                        "complexity": plan.get("complexity", "medium"),
                        "urgency": plan.get("urgency", "low"),
                        "risk_level": plan.get("risk_level", "low"),
                        "requires_empathy": plan.get("requires_empathy", False),
                    }
            except Exception as e:
                logger.warning(f"Planner LLM failed: {e}")

        return self._fast_plan(message, emotion)


reasoning_service = ReasoningService()
print("✅ Reasoning Service migrated")
