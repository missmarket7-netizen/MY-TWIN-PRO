"""
Reasoning Service v3.0 – مخطط تنفيذ النوايا (متكامل مع TCMA والأدوات الجديدة)
================================================================================
- يخطط للخطوات بناءً على نية المستخدم
- يتكامل مع Unified Tool Registry (الأدوات الجديدة)
- يستخدم TCMA لتحديد الحاجة إلى التعاطف
"""
import os, logging, json, re
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("reasoning_service")

try:
    from app.features.tools.tool_registry import ToolRegistry
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

VALID_INTENTS = {
    "general", "emotional", "coaching", "decision",
    "memory", "search", "weather", "music", "goal",
    "greeting", "gratitude", "goodbye", "news", "coding",
    "business", "career", "planning", "study", "dream",
    "life_coach", "smart_home", "task", "code_lab"
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
        
        # خريطة محدثة للنوايا والأدوات الجديدة
        patterns = {
            "weather": r"\b(طقس|الجو|الرياح|مطر|حرارة|شمس|weather|rain|temperature)\b",
            "news": r"\b(أخبار|حدث|عاجل|news|headlines)\b",
            "search": r"\b(بحث|search|معلومات عن|اعرف)\b",
            "goal": r"\b(هدف|أهداف|تقدم|خطة|plan|goal)\b",
            "memory": r"\b(ذكرت|قلت|اتذكر|remember|memory|سابق)\b",
            "emotional": r"\b(حزين|خايف|قلق|sad|worried|anxious|خوف|مكتئب)\b",
            "greeting": r"\b(مرحبا|اهلا|صباح الخير|hello|hi)\b",
            "goodbye": r"\b(مع السلامة|باي|bye|goodbye)\b",
            "gratitude": r"\b(شكرا|تسلم|thanks|thank you)\b",
            "study": r"\b(ادرس|تعلم|مفهوم|درس|study|learn|concept)\b",
            "code_lab": r"\b(كود|برمجة|تطبيق|code|programming|python|react)\b",
            "dream": r"\b(حلم|حلمت|dream|nightmare)\b",
            "smart_home": r"\b(شغل النور|اطفئ|منزل|home|light)\b",
            "task": r"\b(مهمة|موعد|تذكير|task|reminder|schedule)\b",
        }
        
        for intent_type, pattern in patterns.items():
            if re.search(pattern, msg_lower):
                intent = intent_type
                break

        # خريطة محدثة للأدوات (من Unified Tool Registry)
        tool_map = {
            "weather": "weather",
            "news": "news",
            "search": "search",
            "study": "study",
            "code_lab": "code",
            "dream": "dream",
            "smart_home": "smart_home_command",
            "task": "create_task",
            "memory": "reflections",
            "emotional": "emotional_state",
        }
        
        available_tools = ToolRegistry.list_tools() if TOOLS_AVAILABLE else []
        primary_tool = tool_map.get(intent) if intent in tool_map and tool_map[intent] in available_tools else None
        
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
        # 1. محاولة تحسين التعاطف من TCMA
        if TCMA_AVAILABLE and user_id:
            try:
                tcma_emotion = await get_emotional_state_for_response(user_id, message)
                if tcma_emotion and tcma_emotion.get("current_emotion") in ["sadness", "fear", "frustration"]:
                    emotion["requires_empathy"] = True
            except: pass

        # 2. استخدام المخطط المحلي (Fast Plan) افتراضياً
        return self._fast_plan(message, emotion)


reasoning_service = ReasoningService()
logger.info("✅ Reasoning Service v3.0 initialized")
