"""
MyTwin – Profile Extractor v2.0 (Automatic + Integrated)
- يستخرج شخصية المستخدم، تفضيلاته، معتقداته، وصفاته تلقائياً من المحادثات
- يعمل كل 50 رسالة ويحدث user_profile في consciousness_core
- يخزن النتائج في Supabase
"""
import logging, json, os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("profile_extractor")

class ProfileExtractor:
    def __init__(self):
        self.extraction_counters: Dict[str, int] = {}
        self.extraction_interval = 50  # يستخرج كل 50 رسالة

    async def should_extract(self, user_id: str) -> bool:
        """التحقق من الحاجة لاستخراج الملف الشخصي"""
        count = self.extraction_counters.get(user_id, 0)
        return count >= self.extraction_interval

    async def increment_counter(self, user_id: str):
        self.extraction_counters[user_id] = self.extraction_counters.get(user_id, 0) + 1

    async def reset_counter(self, user_id: str):
        self.extraction_counters[user_id] = 0

    async def extract_from_conversation(self, messages: List[str], multi_client,
                                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        استخراج شخصية المستخدم من المحادثات.
        """
        if not messages:
            return {}

        recent = messages[-30:]  # آخر 30 رسالة
        text = "\n".join(f"- {m}" for m in recent if m)

        prompt = f"""استخرج من هذه المحادثة شخصية المستخدم. أعد ONLY JSON بدون أي نص إضافي:
{{
  "personality_traits": ["صفة 1", "صفة 2"],
  "preferences": ["تفضيل 1"],
  "beliefs": ["اعتقاد 1"],
  "interests": ["اهتمام 1"],
  "communication_style": "رسمي/غير رسمي/عاطفي",
  "confidence": 0.0-1.0
}}

المحادثة:
{text[:2000]}

JSON:"""

        try:
            reply = await multi_client.get_best_reply(prompt)
            if reply:
                import re
                # استخراج JSON من الرد
                match = re.search(r'\{[^{}]*\}', reply)
                if match:
                    data = json.loads(match.group())
                    logger.info(f"✅ تم استخراج شخصية المستخدم: {data.get('personality_traits', [])}")

                    # تخزين في Supabase
                    if user_id:
                        await self._store_profile(user_id, data)

                    return data
        except Exception as e:
            logger.warning(f"Profile extraction failed: {e}")

        return {}

    async def _store_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """تخزين الشخصية المستخرجة في Supabase و consciousness_core"""
        try:
            from supabase import create_client
            db = create_client(
                os.getenv("SUPABASE_URL", ""),
                os.getenv("SUPABASE_SERVICE_KEY", "")
            )

            # تخزين في جدول personality_profiles
            db.table("personality_profiles").insert({
                "user_id": user_id,
                "analyzed_traits": profile_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()

            # تحديث consciousness_core
            try:
                from consciousness_core import consciousness_core
                await consciousness_core.update_user_profile(user_id, {
                    "personality_traits": profile_data.get("personality_traits", []),
                    "preferences": profile_data.get("preferences", []),
                    "communication_style": profile_data.get("communication_style", ""),
                })
            except:
                pass

        except Exception as e:
            logger.warning(f"Failed to store profile: {e}")


profile_extractor = ProfileExtractor()
print("✅ Profile Extractor v2.0 initialized")
