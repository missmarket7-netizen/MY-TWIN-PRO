"""
MyTwin – Reasoning Engine v5.5 (Production Grade LLM Planner)
- Single MultiAIClient instance (reuse)
- Robust JSON extraction (json_repair fallback)
- Fixed _is_simple_chat (exact match)
- Separated intent vs goal
- Plan validation (type checks + fixes)
- Tier-aware tool filtering (cost awareness)
"""
import os, logging, json, re
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("reasoning_engine")

class ToolRegistry:
    _tools: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name, func, priority=5, cost=1, category="general", description=""):
        cls._tools[name] = {
            "function": func,
            "priority": priority,
            "cost": cost,
            "category": category,
            "description": description
        }
    
    @classmethod
    def get_tool(cls, name):
        return cls._tools.get(name, {}).get("function")
    
    @classmethod
    def list_tools(cls):
        return list(cls._tools.keys())
    
    @classmethod
    def get_tool_descriptions(cls, tier: str = "free") -> Dict[str, str]:
        """تصفية الأدوات حسب الباقة (التكلفة)."""
        descriptions = {}
        for name, info in cls._tools.items():
            # ✅ Cost Awareness: إخفاء الأدوات المكلفة عن الباقات المنخفضة
            if tier in ["free", "plus"] and info.get("cost", 1) > 2:
                continue
            descriptions[name] = info.get("description", "")
        return descriptions

# ── تسجيل الأدوات ──────────────────────────────
async def _tool_remind_goal(user_id: str, query: str = "") -> Optional[str]:
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", ""); key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key: return None
        db = create_client(url, key)
        res = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).limit(3).execute()
        if res.data: return "أهدافك النشطة: " + "، ".join(g.get("title", "") for g in res.data)
        return "لا توجد أهداف نشطة حالياً."
    except Exception as e:
        logger.warning(f"Tool remind_goal failed: {e}")
        return None

async def _tool_fetch_memory(user_id: str, query: str = "") -> Optional[str]:
    try:
        from memory_graph import get_memory_context
        context = await get_memory_context(user_id)
        if context and query.lower() in str(context).lower(): return str(context)
        return "لا توجد ذكريات تطابق البحث."
    except Exception as e:
        logger.warning(f"Tool fetch_memory failed: {e}")
        return None

ToolRegistry.register("remind_goal", _tool_remind_goal, 9, 1, "memory", "استرجاع أهداف المستخدم النشطة")
ToolRegistry.register("fetch_memory", _tool_fetch_memory, 8, 1, "memory", "استرجاع ذكريات محددة من الماضي")

try:
    from external_services import (
        search_google, search_youtube, search_spotify,
        get_weather, get_news, get_currency,
        home_assistant_control
    )
    ToolRegistry.register("search_google", search_google, 8, 2, "search", "البحث في الإنترنت عن معلومات عامة")
    ToolRegistry.register("search_youtube", search_youtube, 7, 2, "search", "البحث عن فيديوهات في يوتيوب")
    ToolRegistry.register("search_spotify", search_spotify, 6, 2, "search", "البحث عن أغاني أو موسيقى في سبوتيفاي")
    ToolRegistry.register("get_weather", get_weather, 9, 1, "utility", "معرفة حالة الطقس في مدينة معينة")
    ToolRegistry.register("get_news", get_news, 7, 1, "utility", "جلب آخر الأخبار والمستجدات")
    ToolRegistry.register("get_currency", get_currency, 6, 1, "utility", "معرفة أسعار صرف العملات")
    ToolRegistry.register("home_assistant_control", home_assistant_control, 5, 3, "smart_home", "التحكم في أجهزة المنزل الذكي مثل الإضاءة")
except ImportError:
    logger.warning("External services not available for tool registry")

class ReasoningEngine:
    def __init__(self):
        # ✅ إنشاء العميل مرة واحدة فقط
        try:
            from multi_ai import MultiAIClient
            self.client = MultiAIClient()
        except:
            self.client = None

    def _extract_json(self, text: str) -> Optional[Dict]:
        """استخراج آمن لـ JSON من رد LLM."""
        if not text:
            return None
        text = text.strip()
        
        # إزالة ```json أو ``` المحيطة
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        # محاولة تحليل النص كاملاً
        try:
            return json.loads(text.strip())
        except:
            pass
        
        # محاولة استخراج أطول كائن JSON
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            return json.loads(text[start:end])
        except:
            pass
        
        # محاولة استخدام json_repair إذا كان مثبتاً
        try:
            from json_repair import repair_json
            return json.loads(repair_json(text))
        except:
            pass
        
        return None

    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة خطة الـ LLM وإصلاحها."""
        if not isinstance(plan.get("subgoals"), list):
            plan["subgoals"] = []
        if not isinstance(plan.get("needs_tool"), bool):
            plan["needs_tool"] = False
        if not isinstance(plan.get("tool_confidence"), (int, float)):
            plan["tool_confidence"] = 0.5
        if not isinstance(plan.get("needs_memory"), bool):
            plan["needs_memory"] = False
        if not isinstance(plan.get("response_style"), str):
            plan["response_style"] = "conversational"
        if not isinstance(plan.get("observation"), str):
            plan["observation"] = ""
        if not isinstance(plan.get("replan_if"), str):
            plan["replan_if"] = ""
        if not isinstance(plan.get("goal"), str):
            plan["goal"] = "general_chat"
        if not isinstance(plan.get("intent"), str):
            plan["intent"] = "general"
        return plan

    def _is_simple_chat(self, message: str) -> bool:
        """التحقق مما إذا كانت الرسالة محادثة بسيطة جداً."""
        simple_patterns = [
            "صباح الخير", "مساء الخير", "مرحبا", "هاي", "شكرا", "كيف حالك",
            "تمام", "حبيبي", "تسلم", "ولا يهمك", "hello", "hi", "thanks",
            "good morning", "good evening", "how are you", "bye", "سلام"
        ]
        msg_lower = message.lower().strip()
        return len(msg_lower) < 25 and any(pattern in msg_lower for pattern in simple_patterns)

    async def create_execution_plan(
        self,
        message: str,
        emotion: Dict[str, Any],
        user_id: Optional[str] = None,
        lang: str = "ar",
        context_summary: str = "",
        tier: str = "free"
    ) -> Dict[str, Any]:
        """
        True LLM Planner: ينتج goal, subgoals, tools, steps, tool_confidence.
        """
        # 1. تخطي التخطيط للمحادثات البسيطة
        if self._is_simple_chat(message):
            return {
                "intent": "general_chat",
                "goal": "general_chat",
                "needs_tool": False,
                "primary_tool": None,
                "steps": [],
                "response_style": "conversational",
                "needs_memory": False,
                "tool_confidence": 1.0,
                "observation": "",
                "replan_if": "",
            }

        # 2. بناء prompt متقدم للـ LLM
        tools_desc = ToolRegistry.get_tool_descriptions(tier)  # ✅ تصفية حسب الباقة
        tools_json = json.dumps(tools_desc, ensure_ascii=False)
        
        prompt = f"""أنت مخطط ذكي لرفيق AI. حلل الموقف وخطط للخطوات.
        
السياق الكامل:
{context_summary}

المشاعر الحالية: {emotion.get('primary', 'neutral')}

الأدوات المتاحة (مع وصفها):
{tools_json}

اختر أفضل أداة للهدف. إذا لم تكن هناك أداة مناسبة، اجعل needs_tool=false.
أعد ONLY JSON صالح بالهيكل التالي:
{{
  "intent": "weather/search/memory/emotional/general/...",
  "goal": "الهدف الرئيسي للمستخدم",
  "subgoals": ["خطوة 1", "خطوة 2"],
  "needs_tool": true/false,
  "primary_tool": "اسم الأداة المختارة أو null",
  "tool_confidence": 0.0-1.0,
  "needs_memory": true/false,
  "response_style": "conversational/informative/supportive/coaching",
  "observation": "ما الذي يجب ملاحظته من نتيجة الأداة؟",
  "replan_if": "شرط إعادة التخطيط"
}}

رسالة المستخدم: "{message}"
JSON:"""
        
        # 3. محاولة استخدام LLM
        if self.client:
            try:
                raw_reply = await self.client.get_best_reply(prompt, task="deep_reasoning")
                plan = self._extract_json(raw_reply)
                if plan:
                    plan = self._validate_plan(plan)  # ✅ تحقق من الصحة
                    
                    # التحقق من وجود الأداة
                    primary_tool = plan.get("primary_tool")
                    if primary_tool and primary_tool not in ToolRegistry.list_tools():
                        logger.warning(f"Invalid tool suggested: {primary_tool}")
                        primary_tool = None
                        plan["needs_tool"] = False

                    # التحقق من Tool Confidence
                    tool_confidence = float(plan.get("tool_confidence", 1.0))
                    if tool_confidence < 0.6 and plan.get("needs_tool"):
                        plan["needs_tool"] = False
                        plan["primary_tool"] = None

                    return {
                        "intent": plan.get("intent", "general"),
                        "goal": plan.get("goal", "general_chat"),
                        "subgoals": plan.get("subgoals", []),
                        "needs_tool": plan.get("needs_tool", False),
                        "primary_tool": primary_tool,
                        "steps": plan.get("subgoals", []),
                        "response_style": plan.get("response_style", "conversational"),
                        "needs_memory": plan.get("needs_memory", False),
                        "tool_confidence": tool_confidence,
                        "observation": plan.get("observation", ""),
                        "replan_if": plan.get("replan_if", ""),
                    }
            except Exception as e:
                logger.warning(f"Planner LLM failed, falling back to keyword detection: {e}")
        
        # 4. Fallback بسيط
        intent = "general"
        msg_lower = message.lower()
        if any(kw in msg_lower for kw in ["طقس", "الجو", "الرياح", "مطر", "حرارة"]): intent = "weather"
        elif any(kw in msg_lower for kw in ["يوتيوب", "فيديو"]): intent = "video"
        elif any(kw in msg_lower for kw in ["أخبار", "news"]): intent = "news"
        elif any(kw in msg_lower for kw in ["عملة", "دولار", "ريال", "سعر"]): intent = "currency"
        elif any(kw in msg_lower for kw in ["أغنية", "موسيقى", "سبوتيفاي"]): intent = "music"
        elif any(kw in msg_lower for kw in ["بحث", "search", "google"]): intent = "search"
        elif any(kw in msg_lower for kw in ["هدف", "أهداف", "تقدم"]): intent = "goal"
        elif any(kw in msg_lower for kw in ["ذكرت", "قلت", "اتذكر", "remember"]): intent = "memory"
        elif any(kw in msg_lower for kw in ["حزين", "خايف", "قلق", "sad", "worried", "anxious"]): intent = "emotional"
        
        tool_map = {
            "weather": "get_weather", "video": "search_youtube", "news": "get_news",
            "currency": "get_currency", "music": "search_spotify", "search": "search_google",
            "goal": "remind_goal", "memory": "fetch_memory"
        }
        return {
            "intent": intent,
            "goal": intent,
            "needs_tool": intent in tool_map and tool_map[intent] in ToolRegistry.list_tools(),
            "primary_tool": tool_map.get(intent),
            "steps": [],
            "response_style": "informative" if intent != "general" else "conversational",
            "needs_memory": intent in ["memory", "emotional"],
            "tool_confidence": 0.8,
            "observation": "",
            "replan_if": "",
        }

    async def plan(self, message, emotion):
        return await self.create_execution_plan(message, emotion)


reasoning_engine = ReasoningEngine()
print("✅ Reasoning Engine v5.5 (Production Grade)")
