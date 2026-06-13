"""
MyTwin – Tool Router v2.1 (يوتيوب أساسي، سبوتيفاي احتياطي)
"""
import logging
from typing import Optional, Dict, Any
from reasoning_engine import reasoning_engine, ToolRegistry

logger = logging.getLogger("tool_router")

class ToolRouter:
    async def route(self, message: str, user_id: str, tier: str = "free",
                    user_profile: Optional[Dict[str, Any]] = None,
                    emotion: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not message:
            return None

        emotion_data = emotion or {"primary": "neutral", "secondary": "neutral", "intensity": 0.5, "valence": 0.0, "arousal": 0.0}
        plan = await reasoning_engine.plan(message=message, emotion=emotion_data, user_id=user_id)

        intent = plan.get("intent", "general")
        selected_tools = plan.get("selected_tools", [])
        confidence = plan.get("intent_confidence", 0)

        logger.info(f"🧠 النية: {intent} (ثقة: {confidence:.2f}) | الأدوات: {selected_tools}")

        if not selected_tools:
            return await self._manual_route(message, user_id, tier, user_profile)

        for tool_name in selected_tools:
            result = await self._execute_tool(tool_name, message, user_id, tier, user_profile)
            if result:
                return result

        return None

    async def _execute_tool(self, tool_name: str, message: str, user_id: str,
                            tier: str, user_profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
        tool_func = ToolRegistry.get_tool(tool_name)
        if not tool_func:
            return None

        try:
            if tool_name == "get_weather":
                city = self._extract_city(message) or "Cairo"
                return await tool_func(city=city, user_id=user_id, tier=tier)

            # ✅ الموسيقى: يوتيوب أولاً
            elif tool_name == "search_youtube":
                query = self._extract_query(message)
                return await tool_func(query, user_id=user_id, tier=tier)

            # ✅ سبوتيفاي احتياطي (يُستدعى فقط إذا فشل يوتيوب)
            elif tool_name == "search_spotify":
                query = self._extract_query(message)
                youtube_tool = ToolRegistry.get_tool("search_youtube")
                if youtube_tool:
                    yt_result = await youtube_tool(query, user_id=user_id, tier=tier)
                    if yt_result and "لم أجد" not in yt_result:
                        return yt_result
                return await tool_func(query, user_id=user_id, tier=tier)

            elif tool_name == "search_google":
                query = self._extract_query(message)
                return await tool_func(query, user_id=user_id, tier=tier)

            elif tool_name == "get_news":
                return await tool_func(user_id=user_id, tier=tier)

            elif tool_name == "get_currency":
                return await tool_func()

            elif tool_name == "home_assistant_control":
                entity_id = user_profile.get("home_entity_id") if user_profile else None
                return await tool_func(message, entity_id=entity_id)

            elif tool_name in ["remind_goal", "analyze_progress", "fetch_memory"]:
                return await tool_func(user_id, query=message)

            else:
                return await tool_func(user_id)

        except Exception as e:
            logger.error(f"فشل تنفيذ {tool_name}: {e}")
            return None

    async def _manual_route(self, message: str, user_id: str, tier: str,
                            user_profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
        msg = message.lower()

        # الطقس
        if any(kw in msg for kw in ["طقس", "الجو", "درجة الحرارة", "الرياح", "مطر", "حر", "برد", "weather"]):
            city = self._extract_city(message) or "Cairo"
            tool = ToolRegistry.get_tool("get_weather")
            if tool: return await tool(city=city, user_id=user_id, tier=tier)

        # ✅ الموسيقى والفيديو: يوتيوب أساسي
        if any(kw in msg for kw in ["يوتيوب", "فيديو", "youtube", "video", "أغنية", "موسيقى", "spotify", "music", "song", "شغل", "play"]):
            query = self._extract_query(message)
            tool = ToolRegistry.get_tool("search_youtube")
            if tool:
                result = await tool(query, user_id=user_id, tier=tier)
                if result and "لم أجد" not in result:
                    return result
            # احتياطي: سبوتيفاي
            tool = ToolRegistry.get_tool("search_spotify")
            if tool: return await tool(query, user_id=user_id, tier=tier)

        # بحث جوجل
        if any(kw in msg for kw in ["بحث", "ابحث", "جوجل", "google", "search"]):
            tool = ToolRegistry.get_tool("search_google")
            if tool: return await tool(self._extract_query(message), user_id=user_id, tier=tier)

        # الأخبار
        if any(kw in msg for kw in ["أخبار", "news", "عاجل"]):
            tool = ToolRegistry.get_tool("get_news")
            if tool: return await tool(user_id=user_id, tier=tier)

        # العملات
        if any(kw in msg for kw in ["عملة", "دولار", "ريال", "جنيه", "يورو", "currency", "exchange", "سعر"]):
            tool = ToolRegistry.get_tool("get_currency")
            if tool: return await tool()

        # المنزل الذكي
        if any(kw in msg for kw in ["منزل", "إضاءة", "home", "light", "تشغيل", "إطفاء"]):
            tool = ToolRegistry.get_tool("home_assistant_control")
            if tool:
                entity_id = user_profile.get("home_entity_id") if user_profile else None
                return await tool(message, entity_id=entity_id)

        # أهداف
        if any(kw in msg for kw in ["هدف", "أهداف", "خطة", "تقدم", "progress", "goal"]):
            tool = ToolRegistry.get_tool("remind_goal")
            if tool: return await tool(user_id, query=message)

        # ذاكرة
        if any(kw in msg for kw in ["ذكرت", "قلت", "اتذكر", "remember", "told"]):
            tool = ToolRegistry.get_tool("fetch_memory")
            if tool: return await tool(user_id, query=message)

        return None

    def _extract_city(self, text: str) -> Optional[str]:
        cities = ["القاهرة", "الإسكندرية", "الرياض", "جدة", "دبي", "أبوظبي", "الدوحة", "مسقط", "المنامة",
                  "بغداد", "دمشق", "عمان", "بيروت", "الخرطوم", "طرابلس", "تونس", "الجزائر", "الرباط", "الكويت",
                  "صنعاء", "مكة", "المدينة", "القدس", "غزة", "اسطنبول", "لندن", "نيويورك", "باريس", "برلين"]
        for city in cities:
            if city in text: return city
        return None

    def _extract_query(self, text: str) -> str:
        command_words = ["بحث", "ابحث", "بحث عن", "search", "search for", "يوتيوب", "youtube",
                        "سبوتيفاي", "spotify", "شغل", "play", "اعرض", "show", "أغنية", "موسيقى", "فيديو"]
        query = text
        for word in command_words: query = query.replace(word, "")
        return query.strip() or text

tool_router = ToolRouter()
