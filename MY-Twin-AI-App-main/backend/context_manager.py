"""
MyTwin – Context Manager v3.2 (Production Ready)
- كاش للوعي والتعلق لتجنب استدعاءات Supabase المكلفة
- دعم تصفية السياق حسب النية (Intent-Based Context)
- قص ذكي للمحتوى مع إشارات بصرية (...)
- آلية تنظيف للكاش لمنع تسرب الذاكرة
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("context_manager")

try:
    from memory_retriever import memory_retriever
except ImportError:
    memory_retriever = None
try:
    from relationship_engine import relationship_engine
except ImportError:
    relationship_engine = None
try:
    from consciousness_core import consciousness_core
except ImportError:
    consciousness_core = None
try:
    from attachment_engine import attachment_engine
except ImportError:
    attachment_engine = None

class ContextManager:
    def __init__(self):
        self.max_memory_items = 5
        self.max_history_items = 10
        self.max_tool_results = 3
        self.token_budget = {
            "memories": 400,
            "history": 300,
            "tools": 200,
        }
        self._consciousness_cache: Dict[str, Dict[str, Any]] = {}
        self._consciousness_cache_time: Dict[str, datetime] = {}
        self._attachment_cache: Dict[str, Dict[str, Any]] = {}
        self._attachment_cache_time: Dict[str, datetime] = {}

    async def _get_cached_consciousness_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        if user_id in self._consciousness_cache and user_id in self._consciousness_cache_time:
            if (now - self._consciousness_cache_time[user_id]).total_seconds() < 60:
                return self._consciousness_cache[user_id]
        if consciousness_core:
            try:
                await consciousness_core.load_state(user_id)
                state = consciousness_core.user_states.get(user_id, {})
                self._consciousness_cache[user_id] = state
                self._consciousness_cache_time[user_id] = now
                # تنظيف الكاش إذا كبر
                if len(self._consciousness_cache) > 1000:
                    oldest = sorted(self._consciousness_cache_time.items(), key=lambda x: x[1])[:100]
                    for uid, _ in oldest:
                        self._consciousness_cache.pop(uid, None)
                        self._consciousness_cache_time.pop(uid, None)
                return state
            except Exception as e:
                logger.warning(f"Failed to load consciousness state: {e}")
        return None

    async def _get_cached_attachment_style(self, user_id: str, recent_texts: List[str]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        if user_id in self._attachment_cache and user_id in self._attachment_cache_time:
            if (now - self._attachment_cache_time[user_id]).total_seconds() < 600:
                return self._attachment_cache[user_id]
        if attachment_engine:
            try:
                att_info = await attachment_engine.detect_attachment_style(user_id, recent_texts)
                self._attachment_cache[user_id] = att_info
                self._attachment_cache_time[user_id] = now
                return att_info
            except Exception as e:
                logger.warning(f"Attachment detection failed: {e}")
        return {}

    async def build_context(self, user_id, message, emotion, history=None, tool_results=None, lang="ar", tier="free", user_profile=None, intent="general"):
        context = {
            "user_profile": {},
            "relationship": {},
            "emotional_state": {},
            "memories": [],
            "recent_conversation": [],
            "tool_results": [],
            "attachment": {},
            "consciousness": {},
            "current_message": message,
            "language": lang,
            "tier": tier,
        }

        # 1. Profile
        if user_profile:
            context["user_profile"] = {
                "name": user_profile.get("full_name", "صديقي"),
                "twin_name": user_profile.get("twin_name", "MyTwin"),
                "lang": lang, "tier": tier,
            }

        # 2. Relationship
        if relationship_engine and user_id:
            try:
                rel_summary = relationship_engine.get_relationship_summary()
                context["relationship"] = {
                    "bond_level": rel_summary.get("bond_level", 0),
                    "stage": rel_summary.get("stage", "stranger"),
                }
            except Exception as e:
                logger.warning(f"Relationship failed: {e}")

        # 3. Emotional State
        if emotion:
            context["emotional_state"] = {
                "primary": emotion.get("primary", "neutral"),
                "intensity": emotion.get("intensity", 0.5),
            }

        # 4. Memories (مدعومة بالنية)
        if memory_retriever and user_id:
            try:
                # ✅ تمرير النية لاسترجاع ذكريات مخصصة
                result = await memory_retriever.retrieve_and_summarize(message, user_id, self.max_memory_items, intent=intent)
                memories = result.get("memories", [])
                context["memories"] = [
                    {
                        "content": m.get("content", ""),
                        "scores": m.get("scores", {}),
                        "memory_type": m.get("memory_type", ""),
                        "emotion": m.get("emotion", ""),
                        "is_hard": m.get("memory_type") == "core",
                    }
                    for m in memories
                ]
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")

        # 5. History
        if history:
            context["recent_conversation"] = history[-self.max_history_items:]

        # 6. Tool Results (قص مع إشارة)
        if tool_results:
            truncated = [self._truncate(t, 300) for t in tool_results[-self.max_tool_results:]]
            context["tool_results"] = truncated

        # 7. Consciousness (مع كاش)
        if consciousness_core and user_id:
            try:
                state = await self._get_cached_consciousness_state(user_id)
                if state:
                    objectives = state.get("active_objectives", [])
                    last_thought = (state.get("internal_state", {}).get("last_thought", "") or "")[:200]
                    context["consciousness"] = {
                        "active_goals": [o.get("title") for o in objectives[:3] if isinstance(o, dict)],
                        "last_thought": last_thought,
                    }
            except Exception as e:
                logger.warning(f"Consciousness failed: {e}")

        # 8. Attachment (مع كاش)
        if user_id and history:
            try:
                recent_texts = [h.get("content", "") for h in history[-20:] if isinstance(h, dict)]
                att_info = await self._get_cached_attachment_style(user_id, recent_texts)
                context["attachment"] = {"style": att_info.get("style"), "confidence": att_info.get("confidence")}
            except Exception as e:
                logger.warning(f"Attachment failed: {e}")

        # ✅ تفعيل compress_context
        context = self.compress_context(context)

        # 9. إضافة planner_summary
        context["planner_summary"] = self.build_context_summary(context)

        return context

    def build_context_summary(self, context: Dict[str, Any]) -> str:
        parts = []
        user = context.get("user_profile", {})
        if user:
            parts.append(f"المستخدم: {user.get('name', '')} (الباقة: {user.get('tier', '')})")

        rel = context.get("relationship", {})
        if rel:
            parts.append(f"العلاقة: مستوى الرابطة {rel.get('bond_level', 0):.0f}%، المرحلة: {rel.get('stage', '')}")

        emo = context.get("emotional_state", {})
        if emo:
            parts.append(f"المشاعر الحالية: {emo.get('primary', '')} (شدة: {emo.get('intensity', 0):.1f})")

        memories = context.get("memories", [])
        if memories:
            sorted_memories = sorted(memories, key=lambda x: x.get("scores", {}).get("final", 0), reverse=True)
            memory_lines = []
            for m in sorted_memories[:3]:
                hard = "[مهم]" if m.get("is_hard") else ""
                content = m.get('content', '')[:150]
                memory_lines.append(f"- {hard} {content}")
            parts.append("ذكريات هامة:\n" + "\n".join(memory_lines))

        history = context.get("recent_conversation", [])
        if history:
            last_messages = history[-3:]
            history_lines = []
            for msg in last_messages:
                role = "المستخدم" if msg.get("role") == "user" else "التوأم"
                content = (msg.get("content", "") or "")[:100]
                history_lines.append(f"{role}: {content}")
            parts.append("آخر المحادثة:\n" + "\n".join(history_lines))

        tools = context.get("tool_results", [])
        if tools:
            truncated_tools = [self._truncate(t, 200) for t in tools]
            parts.append("نتائج الأدوات السابقة:\n" + "\n".join(truncated_tools))

        cons = context.get("consciousness", {})
        if cons.get("active_goals") or cons.get("last_thought"):
            goals = ', '.join(cons.get('active_goals', []))
            thought = cons.get('last_thought', '')[:150]
            parts.append(f"أهداف نشطة: {goals}. آخر فكرة للتوأم: {thought}")

        att = context.get("attachment", {})
        if att.get("style") and att.get("style") != "unknown":
            parts.append(f"نمط التعلق: {att.get('style')}")

        return "\n".join(parts)

    def format_context_for_prompt(self, context: Dict[str, Any], lang: str = "ar") -> str:
        parts = []
        if context.get("tool_results"):
            truncated = [self._truncate(t, 250) for t in context["tool_results"]]
            parts.append("<TOOL_RESULTS>\n" + "\n".join(truncated) + "\n</TOOL_RESULTS>")
        if context.get("memories"):
            sorted_memories = sorted(context["memories"], key=lambda x: x.get("scores", {}).get("final", 0), reverse=True)
            mem_lines = []
            for m in sorted_memories:
                hard = "[مهم]" if m.get("is_hard") else ""
                content = self._truncate(m.get('content', ''), 200)
                mem_lines.append(f"- {hard} {content} (أهمية: {m.get('scores', {}).get('final', 0):.2f})")
            parts.append("<RELEVANT_MEMORIES>\n" + "\n".join(mem_lines) + "\n</RELEVANT_MEMORIES>")
        if context.get("recent_conversation"):
            lines = []
            for msg in context["recent_conversation"]:
                role = "المستخدم" if msg.get("role") == "user" else "التوأم" if lang == "ar" else "User" if msg.get("role") == "user" else "Twin"
                content = self._truncate(msg.get("content", "") or "", 150)
                lines.append(f"{role}: {content}")
            parts.append("<RECENT_CONVERSATION>\n" + "\n".join(lines) + "\n</RECENT_CONVERSATION>")
        rel = context.get("relationship", {})
        if rel:
            label = f"مستوى الرابطة: {rel.get('bond_level', 0):.0f}%" if lang == "ar" else f"Bond: {rel.get('bond_level', 0):.0f}%"
            parts.append(f"<RELATIONSHIP> {label} </RELATIONSHIP>")
        cons = context.get("consciousness", {})
        if cons.get("active_goals") or cons.get("last_thought"):
            goals = ', '.join(cons.get('active_goals', []))
            thought = cons.get('last_thought', '')[:150]
            parts.append(f"<CONSCIOUSNESS> Goals: {goals}; Thought: {thought} </CONSCIOUSNESS>")
        return "\n".join(parts)

    def compress_context(self, context: Dict[str, Any], max_tokens: int = 2000) -> Dict[str, Any]:
        memories = context.get("memories", [])
        while memories and len("\n".join([m.get("content", "") for m in memories])) // 4 > self.token_budget["memories"]:
            memories.pop(-1)
        context["memories"] = memories

        history = context.get("recent_conversation", [])
        while history and len("\n".join([h.get("content", "") for h in history])) // 4 > self.token_budget["history"]:
            history.pop(0)
        context["recent_conversation"] = history

        tools = context.get("tool_results", [])
        while tools and len("\n".join(tools)) // 4 > self.token_budget["tools"]:
            tools.pop(-1)
        context["tool_results"] = tools

        return context

    def _truncate(self, text: str, max_len: int) -> str:
        if len(text) > max_len:
            return text[:max_len] + "..."
        return text

    # ========== دوال تصفية السياق (جديدة) ==========
    def filter_by_intent(self, context: Dict[str, Any], intent: str) -> str:
        """
        تُرجع سياقاً نصياً مُصفى حسب النية.
        مثلاً: للمشاعر، نُرجع الذكريات والتعلق فقط.
        """
        if intent in ["emotional", "coaching"]:
            parts = []
            memories = context.get("memories", [])
            if memories:
                mem_lines = [self._truncate(m.get('content', ''), 200) for m in memories[:3]]
                parts.append("<RELEVANT_MEMORIES>\n" + "\n".join(mem_lines) + "\n</RELEVANT_MEMORIES>")
            rel = context.get("relationship", {})
            if rel:
                label = f"Bond: {rel.get('bond_level', 0):.0f}%"
                parts.append(f"<RELATIONSHIP> {label} </RELATIONSHIP>")
            return "\n".join(parts)
        return self.format_context_for_prompt(context)

    def filter_history_by_intent(self, history: List[Dict], intent: str) -> List[Dict]:
        """تصفية التاريخ حسب النية (حالياً ترجع آخر 4 رسائل فقط)"""
        if not history:
            return []
        return history[-4:]


context_manager = ContextManager()
print("✅ Context Manager v3.2 (Production Ready)")
