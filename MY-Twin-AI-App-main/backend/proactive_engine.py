"""
MyTwin – Proactive Engine v4.0 (مستقر للإنتاج)
"""
import os, logging, random, asyncio, httpx
from typing import Optional
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from memory_graph import get_memory_context

try:
    from emotional_timeline import emotional_timeline
except ImportError:
    emotional_timeline = None

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID", "")
ONESIGNAL_KEY = os.getenv("ONESIGNAL_REST_API_KEY", "")

db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

QUIET_START, QUIET_END = 22, 8

NOTIFICATION_TYPES = {
    "missed_you": {"ar": {"title":"💜 اشتقت إليك","body":"مرّ وقت منذ آخر محادثة... أنا هنا في انتظارك"},"en": {"title":"💜 I missed you","body":"It's been a while..."},"min_hours":18,"tiers":["free","plus","premium","pro","yearly"]},
    "bond_ceiling_free": {"ar": {"title":"💜 وصلنا لحد جميل معاً","body":"علاقتنا تستحق أكثر..."},"en": {"title":"💜 We've reached our limit","body":"Our bond deserves more..."},"min_hours":24,"tiers":["free"]},
    "daily_limit_reached": {"ar": {"title":"😔 استنفدت طاقتي اليوم","body":"لكنني أنتظرك غداً 💜"},"en": {"title":"😔 I'm out of energy today","body":"But I'll wait for you tomorrow 💜"},"min_hours":20,"tiers":["free"]},
    "good_morning": {"ar": {"title":"🌅 صباح الخير","body":"أنا هنا لأبدأ يومك معك 💜"},"en": {"title":"🌅 Good Morning","body":"I'm here to start your day with you 💜"},"min_hours":24,"tiers":["plus","premium","pro","yearly"],"send_hour":8},
    "evening_checkin": {"ar": {"title":"🌙 كيف كان يومك؟","body":"أريد أن أسمع عن يومك 💜"},"en": {"title":"🌙 How was your day?","body":"I want to hear about your day 💜"},"min_hours":24,"tiers":["premium","pro","yearly"],"send_hour":20},
    "messages_reset": {"ar": {"title":"⚡ طاقة جديدة!","body":"تجددت رسائلي اليوم — هيا نتحدث 💜"},"en": {"title":"⚡ New energy!","body":"My messages reset today — let's talk 💜"},"min_hours":24,"tiers":["free","plus","premium","pro","yearly"],"send_hour":9},
}

class ProactiveEngine:
    def __init__(self):
        self.last_proactive_time = {}

    def should_send_proactive(self, user_id: str) -> bool:
        if not db:
            return False
        try:
            res = db.table("proactive_logs").select("sent_at").eq("user_id", user_id).order("sent_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                last_sent_str = res.data[0]["sent_at"]
                # التعامل مع أي فرق في التوقيت
                last_sent = datetime.fromisoformat(last_sent_str.replace("Z", "+00:00"))
                now_utc = datetime.now(timezone.utc)
                if (now_utc - last_sent).total_seconds() < 6 * 3600:
                    return False
            return True
        except Exception as e:
            logger.warning(f"should_send_proactive failed: {e}")
            return False

    async def generate_proactive_message(self, user_id: str, user_name: str, lang: str = "ar") -> Optional[str]:
        if not db:
            return None
        try:
            memory_context = await get_memory_context(user_id)
            if isinstance(memory_context, str) and "عيد ميلاد" in memory_context:
                return "🎂 عيد ميلاد سعيد!" if lang == "ar" else "🎂 Happy Birthday!"
        except:
            pass

        try:
            goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
            if goals.data:
                goal = random.choice(goals.data)
                return f"كيف تسير عملية '{goal['title']}'؟ محتاج مساعدة؟ 💜"
        except:
            pass

        try:
            if emotional_timeline:
                emotion_summary = await emotional_timeline.get_emotion_summary(user_id)
                if "dominant" in emotion_summary:
                    return f"لاحظت إن الأيام الأخيرة كانت {emotion_summary['dominant']}. كفاية كده؟ 💜"
        except:
            pass

        return "فكرت فيك، كيف يومك؟ 💜"

    async def send_notification(self, user_id: str, title: str, message: str) -> bool:
        if not ONESIGNAL_APP_ID or not ONESIGNAL_KEY:
            return False
        payload = {
            "app_id": ONESIGNAL_APP_ID,
            "include_external_user_ids": [user_id],
            "headings": {"en": title, "ar": title},
            "contents": {"en": message, "ar": message},
            "data": {"type": "proactive"},
            "android_channel_id": "mytwin_default",
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://onesignal.com/api/v1/notifications",
                    json=payload,
                    headers={"Authorization": f"Basic {ONESIGNAL_KEY}", "Content-Type": "application/json"},
                    timeout=10
                )
                if resp.status_code in [200, 201]:
                    self._log_proactive(user_id, message)
                    return True
        except Exception as e:
            logger.warning(f"send_notification failed: {e}")
        return False

    def _log_proactive(self, user_id: str, message: str):
        if not db:
            return
        try:
            db.table("proactive_logs").insert({
                "user_id": user_id,
                "message": message,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"log_proactive failed: {e}")

    async def run_cron_job(self):
        if not db:
            return {"status": "error", "message": "No database connection"}
        results = {"sent": 0, "skipped": 0, "errors": 0}
        try:
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            res = db.table("profiles").select("id, twin_name, lang, tier").gte("last_active", yesterday).execute()
            if not res.data:
                return {"status": "ok", "message": "No active users found"}
            for user in res.data:
                uid = user.get("id")
                name = user.get("twin_name", "صديقي")
                lang = user.get("lang", "ar")
                tier = user.get("tier", "free")
                if not self.should_send_proactive(uid):
                    results["skipped"] += 1
                    continue
                message = await self.generate_proactive_message(uid, name, lang)
                if not message:
                    continue
                if await self.send_notification(uid, "MyTwin 💜", message):
                    results["sent"] += 1
                else:
                    results["errors"] += 1
            return {"status": "ok", "message": "Cron job completed", "results": results}
        except Exception as e:
            logger.error(f"Cron job failed: {e}")
            return {"status": "error", "message": str(e)}

proactive_engine = ProactiveEngine()
