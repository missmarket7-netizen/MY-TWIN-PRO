"""
User Model v2.0 – متوافق مع TCMA والهيكل الجديد
==================================================
يجمع بيانات المستخدم من Supabase + TCMA + Personality State.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timezone

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.twin_state.personality_state import get_state_summary
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False

try:
    from app.memory.identity.identity_model import get_identity
    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False

try:
    from app.features.agent_metrics import agent_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger("user_service")

class UserModel:
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        profile = {}
        if DB_AVAILABLE:
            try:
                db = get_db()
                res = db.table("profiles").select("*").eq("id", user_id).single().execute()
                if res.data: profile = res.data
            except: pass

        # حالة من TCMA
        consciousness = {}
        if IDENTITY_AVAILABLE:
            try:
                identity = await get_identity(user_id)
                if identity:
                    consciousness["identity"] = identity
            except: pass
        if PERSONALITY_AVAILABLE:
            try:
                state = await get_state_summary(user_id)
                consciousness["active_objectives"] = state.get("active_objectives", [])
                consciousness["mood"] = state.get("mood", "neutral")
            except: pass

        # إحصائيات
        tool_stats = {}
        if METRICS_AVAILABLE:
            try: tool_stats = await agent_metrics.get_tool_stats(user_id)
            except: pass

        return {
            "profile": profile,
            "consciousness": consciousness,
            "tool_stats": tool_stats,
            "preferences": self._extract_preferences(profile),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_preferences(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "language": profile.get("lang", "ar"),
            "twin_style": profile.get("twin_style", "supportive"),
            "reply_style": profile.get("reply_style", "medium"),
            "voice_personality": profile.get("voice_personality", "friend"),
            "voice_speed": profile.get("voice_speed", 0.9),
            "voice_pitch": profile.get("voice_pitch", 1.0),
            "twin_gender": profile.get("twin_gender", "female"),
        }

user_model = UserModel()
logger.info("✅ User Model v2.0 initialized")
