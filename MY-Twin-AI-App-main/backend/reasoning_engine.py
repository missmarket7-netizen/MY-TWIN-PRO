"""
MyTwin – Reasoning Engine v8.0 (Agent Brain)
- يكتشف النية (Intent) بدون LLM عبر Rules + Keywords
- يدير أدوات متعددة مع أولويات وتكلفة
- يدمج وعي المستخدم (Consciousness)
- يُنتج response_mode لتوجيه MultiAI
- يوفر سياق الأدوات (tool_context) لـ PromptBuilder
"""
import os, logging, re, asyncio, json, time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone

logger = logging.getLogger("reasoning_engine")

# ========== أدوات معرفة مسبقاً مع أولويات ==========
class ToolRegistry:
    _tools: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, func: Callable, priority: int = 5, cost: int = 1, category: str = "general"):
        cls._tools[name] = {
            "function": func,
            "priority": priority,
            "cost": cost,
            "category": category,
        }

    @classmethod
    def get_tool(cls, name: str) -> Optional[Callable]:
        tool = cls._tools.get(name)
        return tool["function"] if tool else None

    @classmethod
    def get_tools_by_category(cls, category: str) -> List[str]:
        return [name for name, info in cls._tools.items() if info["category"] == category]

    @classmethod
    def get_all_tools(cls) -> List[str]:
        return list(cls._tools.keys())

    @classmethod
    def get_tool_info(cls, name: str) -> Optional[Dict]:
        return cls._tools.get(name)

# ========== أدوات حقيقية (مسجلة) ==========
async def _tool_remind_goal(user_id: str, query: str = "") -> Optional[str]:
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key: return None
        db = create_client(url, key)
        res = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).limit(3).execute()
        if res.data:
            goals = [g.get("title", "") for g in res.data]
            return "أهدافك النشطة: " + "، ".join(goals)
        return "لا توجد أهداف نشطة حالياً."
    except Exception as e:
        logger.warning(f"Tool remind_goal failed: {e}")
        return None

async def _tool_analyze_progress(user_id: str, query: str = "") -> Optional[str]:
    try:
        from growth_tracker import get_growth_history
        history = await get_growth_history(user_id, limit=1)
        if history:
            last = history[0]
            return f"آخر تقرير نمو: {last.get('summary', 'لا يوجد')}"
        return "لم يتم تسجيل تقدم بعد."
    except Exception as e:
        logger.warning(f"Tool analyze_progress failed: {e}")
        return None

async def _tool_fetch_memory(user_id: str, query: str = "") -> Optional[str]:
    try:
        from memory_graph import get_memory_context
        context = await get_memory_context(user_id)
        if context and query and query.lower() in str(context).lower():
            return str(context)
        return "لا توجد ذكريات تطابق البحث."
    except Exception as e:
        logger.warning(f"Tool fetch_memory failed: {e}")
        return None

async def _tool_recommend_product(user_id: str, query: str = "") -> Optional[str]:
    try:
        from product_recommender import product_recommender
        intent = await product_recommender.detect_purchase_intent(query, user_id)
        if intent:
            product = await product_recommender.get_best_product(intent, "free")
            if product:
                return product_recommender.format_suggestion(product, "ar")
        return "لا توجد توصيات حالية."
    except Exception as e:
        logger.warning(f"Tool recommend_product failed: {e}")
        return None

async def _tool_smart_home(user_id: str, query: str = "") -> Optional[str]:
    try:
        from smart_home import process_voice_command
        return await process_voice_command(query, user_id, "free")
    except Exception as e:
        logger.warning(f"Tool smart_home failed: {e}")
        return None

async def _tool_weather(user_id: str, query: str = "") -> Optional[str]:
    try:
        from external_services import get_weather
        return await get_weather(city=query)
    except Exception as e:
        logger.warning(f"Tool weather failed: {e}")
        return None

async def _tool_youtube(user_id: str, query: str = "") -> Optional[str]:
    try:
        from external_services import search_youtube
        return await search_youtube(query)
    except Exception as e:
        logger.warning(f"Tool youtube failed: {e}")
        return None

# تسجيل الأدوات
ToolRegistry.register("remind_goal", _tool_remind_goal, priority=9, cost=1, category="memory")
ToolRegistry.register("analyze_progress", _tool_analyze_progress, priority=8, cost=1, category="growth")
ToolRegistry.register("fetch_memory", _tool_fetch_memory, priority=8, cost=1, category="memory")
ToolRegistry.register("recommend_product", _tool_recommend_product, priority=3, cost=2, category="commerce")
ToolRegistry.register("smart_home", _tool_smart_home, priority=3, cost=3, category="home")
ToolRegistry.register("weather", _tool_weather, priority=7, cost=1, category="external")
ToolRegistry.register("youtube", _tool_youtube, priority=6, cost=2, category="external")

# ========== كشف النية بدون LLM ==========
INTENT_KEYWORDS = {
    "goal_tracking": ["هدف", "أهداف", "خطة", "تقدم", "progress", "goal", "target"],
    "memory_retrieval": ["ذكرت", "قلت", "اتذكر", "قبل كده", "remember", "told", "mentioned"],
    "emotional_support": ["حزين", "خايف", "قلق", "متضايق", "sad", "worried", "anxious", "fear", "lonely"],
    "learning": ["علمني", "شرح", "افهم", "دورة", "كورس", "learn", "teach", "explain", "course"],
    "productivity": ["تنظيم", "جدول", "إنتاجية", "وقت", "productivity", "schedule", "plan"],
    "shopping": ["اشتري", "شراء", "منتج", "سعر", "buy", "purchase", "price", "shopping"],
    "search": ["بحث", "معلومات", "ما هو", "من هو", "search", "information", "who is", "what is"],
    "coding": ["كود", "برمجة", "بايثون", "جافا", "code", "python", "programming", "function"],
    "dream": ["حلم", "حلمت", "تفسير", "dream", "nightmare"],
    "home": ["نور", "إضاءة", "مكيف", "light", "ac", "temperature"],
    "general": []
}

def detect_intent(message: str) -> Tuple[str, float]:
    """يكتشف النية من الرسالة باستخدام الكلمات المفتاحية"""
    if not message:
        return "general", 0.0
    msg_lower = message.lower()
    max_score = 0
    best_intent = "general"
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in msg_lower)
        if score > max_score:
            max_score = score
            best_intent = intent
    confidence = min(max_score / 3.0, 1.0) if max_score > 0 else 0.5
    return best_intent, confidence

# ========== المحرك الرئيسي ==========
class ReasoningEngine:
    def __init__(self, gemini_key: Optional[str] = None):
        self.gemini_key = gemini_key
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # ثواني

    def _get_multi_client(self):
        try:
            from multi_ai import MultiAIClient
            return MultiAIClient()
        except:
            return None

    def _get_cached(self, key: str) -> Optional[str]:
        entry = self.context_cache.get(key)
        if entry and time.time() - entry["timestamp"] < self.cache_ttl:
            return entry["value"]
        return None

    def _set_cache(self, key: str, value: str):
        self.context_cache[key] = {"value": value, "timestamp": time.time()}

    async def plan(self, message: str, emotion: Dict[str, Any], consciousness_context: Optional[Dict] = None, user_id: Optional[str] = None, lang: str = "ar") -> Dict[str, Any]:
        """
        يخطط للاستجابة بناءً على النية والأدوات والسياق.
        يُرجع metadata للاستخدام في TwinBrain و PromptBuilder.
        """
        # 1. اكتشاف النية (محلي)
        intent, confidence = detect_intent(message)

        # 2. اختيار الأدوات المناسبة (بدون LLM)
        selected_tools = []
        tool_context = {}

        if intent == "goal_tracking":
            selected_tools = ["remind_goal", "analyze_progress"]
        elif intent == "memory_retrieval":
            selected_tools = ["fetch_memory"]
        elif intent == "shopping":
            selected_tools = ["recommend_product"]
        elif intent == "home":
            selected_tools = ["smart_home"]
        elif intent == "search":
            selected_tools = ["youtube", "weather"]  # weather as fallback
        elif intent == "coding":
            selected_tools = []  # no tool, rely on AI reasoning
        else:
            selected_tools = []

        # 3. تنفيذ الأدوات (متوازي مع التخزين المؤقت)
        if selected_tools and user_id:
            for tool_name in selected_tools:
                cache_key = f"{user_id}:{tool_name}"
                cached = self._get_cached(cache_key)
                if cached:
                    tool_context[tool_name] = cached
                    continue
                tool_func = ToolRegistry.get_tool(tool_name)
                if tool_func:
                    try:
                        loop = asyncio.get_running_loop()
                        result = await tool_func(user_id, message) if asyncio.iscoroutinefunction(tool_func) else await loop.run_in_executor(None, tool_func, user_id, message)
                        if result:
                            self._set_cache(cache_key, result)
                            tool_context[tool_name] = result
                    except Exception as e:
                        logger.warning(f"Tool {tool_name} failed: {e}")

        # 4. تحديد وضع الاستجابة (response_mode) لـ MultiAI
        response_mode_map = {
            "emotional_support": "emotional",
            "coding": "coding",
            "learning": "general",
            "search": "search",
            "goal_tracking": "coaching",
            "memory_retrieval": "general",
            "shopping": "general",
            "home": "agent",
            "dream": "dream",
            "general": "general"
        }
        response_mode = response_mode_map.get(intent, "general")

        # 5. وزن المشاعر
        emotion_primary = emotion.get("primary", "neutral")
        emotion_weight = 0.5
        if emotion_primary in ["sadness", "fear", "anger"]:
            emotion_weight = 0.8
            response_mode = "emotional"  # override for strong emotions
        elif emotion_primary in ["joy", "love"]:
            emotion_weight = 0.6

        return {
            "intent": intent,
            "intent_confidence": confidence,
            "response_mode": response_mode,
            "emotion_weight": emotion_weight,
            "selected_tools": selected_tools,
            "tool_context": tool_context if tool_context else "",
            "reasoning_depth": "medium",
        }

    async def execute_plan(self, plan: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """تنفيذ خطة الأدوات (استدعاء خارجي)"""
        return await self.plan(plan.get("message", ""), plan.get("emotion", {}), user_id=user_id)

    async def reflect(self, plan: Dict[str, Any], result: str, lang: str = "ar") -> Dict[str, Any]:
        return {"was_effective": True, "what_worked": "", "what_didnt": "", "adjustment": ""}


# نسخة عالمية
reasoning_engine = ReasoningEngine()
logger.info("✅ Reasoning Engine v8.0 (Agent Brain) initialized")
