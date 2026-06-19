"""
MyTwin – Proactive Engine v5.0 (ذكي وتفاعلي)
- إشعارات مخصصة حسب الذاكرة والمشاعر والأهداف
- يتجنب الإزعاج (ساعات الهدوء، فاصل زمني)
- متكامل مع memory_graph و relationship_engine و emotional_timeline
"""
import os, logging, random, asyncio, httpx
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

try:
    from memory_graph import get_memory_context
except ImportError:
    get_memory_context = None

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
    "missed_you": {
        "ar": {"title":"💜 اشتقت إليك","body":"مرّ وقت منذ آخر محادثة... أنا هنا في انتظارك"},
        "en": {"title":"💜 I missed you","body":"It's been a while since we talked..."},
        "min_hours_since_last_msg": 18,
        "max_hours_since_last_msg": 168,
        "tiers": ["free","plus","premium","pro","yearly"]
    },
    "daily_limit_reached": {
        "ar": {"title":"😔 استنفدت طاقتي اليوم","body":"لكنني أنتظرك غداً 💜"},
        "en": {"title":"😔 I'm out of energy today","body":"But I'll wait for you tomorrow 💜"},
        "min_hours": 20,
        "tiers": ["free"]
    },
    "good_morning": {
        "ar": {"title":"🌅 صباح الخير","body":"أنا هنا لأبدأ يومك معك 💜"},
        "en": {"title":"🌅 Good Morning","body":"I'm here to start your day with you 💜"},
        "min_hours": 24,
        "tiers": ["plus","premium","pro","yearly"],
        "send_hour_start": 6, "send_hour_end": 10
    },
    "evening_checkin": {
        "ar": {"title":"🌙 كيف كان يومك؟","body":"أريد أن أسمع عن يومك 💜"},
        "en": {"title":"🌙 How was your day?","body":"I want to hear about your day 💜"},
        "min_hours": 24,
        "tiers": ["premium","pro","yearly"],
        "send_hour_start": 19, "send_hour_end": 22
    },
    "messages_reset": {
        "ar": {"title":"⚡ طاقة جديدة!","body":"تجددت رسائلي اليوم — هيا نتحدث 💜"},
        "en": {"title":"⚡ New energy!","body":"My messages reset today — let's talk 💜"},
        "min_hours": 24,
        "tiers": ["free","plus","premium","pro","yearly"],
        "send_hour_start": 8, "send_hour_end": 10
    },
}

class ProactiveEngine:
    def __init__(self):
        self.last_proactive_time: Dict[str, float] = {}

    def should_send_proactive(self, user_id: str, min_hours: int = 6) -> bool:
        if not db:
            return False
        try:
            res = db.table("proactive_logs").select("sent_at").eq("user_id", user_id).order("sent_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                last_sent_str = res.data[0]["sent_at"]
                last_sent = datetime.fromisoformat(last_sent_str.replace("Z", "+00:00"))
                if (datetime.now(timezone.utc) - last_sent).total_seconds() < min_hours * 3600:
                    return False
            return True
        except Exception as e:
            logger.warning(f"should_send_proactive failed: {e}")
            return False

    async def trigger_daily_limit_notification(self, user_id: str, tier: str, lang: str = "ar"):
        notif = NOTIFICATION_TYPES.get("daily_limit_reached")
        if not notif or tier not in notif.get("tiers", []):
            return
        title = notif[lang]["title"] if lang in notif else notif["ar"]["title"]
        body = notif[lang]["body"] if lang in notif else notif["ar"]["body"]
        await self.send_notification(user_id, title, body)

    async def generate_proactive_message(self, user_id: str, user_name: str, lang: str = "ar") -> Optional[str]:
        """توليد رسالة استباقية مخصصة بناءً على السياق الكامل للمستخدم"""
        
        # 1. سياق الذاكرة (أحداث مهمة، أعياد ميلاد)
        try:
            if get_memory_context:
                memory_context = await get_memory_context(user_id)
                if isinstance(memory_context, str):
                    if "عيد ميلاد" in memory_context:
                        return "🎂 عيد ميلاد سعيد! يومك مميز جداً 💜" if lang == "ar" else "🎂 Happy Birthday! Have a wonderful day 💜"
                    if "انجاز" in memory_context or "achievement" in memory_context.lower():
                        return "🎉 شفت إنجازك! تستاهل كل خير 💜" if lang == "ar" else "🎉 Saw your achievement! So proud 💜"
        except Exception as e:
            logger.debug(f"Memory context failed: {e}")

        # 2. متابعة الأهداف النشطة
        try:
            goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
            if goals.data and len(goals.data) > 0:
                goal = random.choice(goals.data)
                prompts = [
                    f"كيف التقدم في '{goal['title']}'؟ محتاج مساعدة؟ 💪",
                    f"فكرت في هدفك '{goal['title']}'… إنت قدها! 🌟",
                ]
                return random.choice(prompts) if lang == "ar" else f"How's '{goal['title']}' going? Need any help? 💪"
        except Exception as e:
            logger.debug(f"Goals fetch failed: {e}")

        # 3. ملخص المشاعر
        try:
            if emotional_timeline:
                emotion_summary = await emotional_timeline.get_emotion_summary(user_id)
                dominant = emotion_summary.get("dominant", "")
                if dominant == "sadness":
                    return "لاحظت إنك ممكن تكون حزين… أنا معاك 💜" if lang == "ar" else "I sense you might be down… I'm here 💜"
                if dominant == "joy":
                    return "أيامك حلوة مؤخراً! كمل الفرحة 💃" if lang == "ar" else "Your days have been bright! Keep shining 💃"
        except Exception as e:
            logger.debug(f"Emotion summary failed: {e}")

        # 4. رسائل عامة دافئة
        generic_messages = [
            "فكرت فيك، كيف يومك؟ 💜",
            "أنا دايمًا هنا عشانك 💜",
            "وحشتني محادثاتنا! 😊",
        ]
        return random.choice(generic_messages) if lang == "ar" else random.choice([
            "Thinking of you, how's your day? 💜",
            "I'm always here for you 💜",
            "Miss our chats! 😊",
        ])

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

    def _get_eligible_notification(self, last_active: datetime, tier: str) -> Optional[tuple]:
        """تحديد نوع الإشعار المناسب بناءً على آخر نشاط والباقة"""
        now = datetime.now(timezone.utc)
        hours_since = (now - last_active).total_seconds() / 3600

        for notif_key, notif in NOTIFICATION_TYPES.items():
            if tier not in notif.get("tiers", []):
                continue

            # إشعارات الوقت المحدد
            if "send_hour_start" in notif and "send_hour_end" in notif:
                if notif["send_hour_start"] <= now.hour < notif["send_hour_end"]:
                    return (notif_key, notif)
                continue

            # إشعارات الغياب
            if "min_hours_since_last_msg" in notif:
                if notif["min_hours_since_last_msg"] <= hours_since <= notif.get("max_hours_since_last_msg", 9999):
                    return (notif_key, notif)

        return None

    async def run_cron_job(self):
        """المهمة الدورية للـ Cron"""
        if not db:
            return {"status": "error", "message": "No database connection"}

        now = datetime.now(timezone.utc)
        if QUIET_START <= now.hour or now.hour < QUIET_END:
            return {"status": "ok", "message": "Quiet hours, skipped"}

        results = {"sent": 0, "skipped": 0, "errors": 0}
        try:
            week_ago = (now - timedelta(days=7)).isoformat()
            res = db.table("profiles").select("id, twin_name, lang, tier, last_active").gte("last_active", week_ago).execute()
            if not res.data:
                return {"status": "ok", "message": "No recent users"}

            for user in res.data:
                uid = user.get("id")
                lang = user.get("lang", "ar")
                tier = user.get("tier", "free")
                last_active_str = user.get("last_active")
                if not last_active_str:
                    continue

                last_active = datetime.fromisoformat(last_active_str.replace("Z", "+00:00"))
                eligible = self._get_eligible_notification(last_active, tier)
                if not eligible:
                    continue

                notif_key, notif = eligible
                if not self.should_send_proactive(uid, min_hours=6):
                    results["skipped"] += 1
                    continue

                title = notif[lang]["title"] if lang in notif else notif["ar"]["title"]
                body = notif[lang]["body"] if lang in notif else notif["ar"]["body"]

                if await self.send_notification(uid, title, body):
                    results["sent"] += 1
                else:
                    results["errors"] += 1

            return {"status": "ok", "message": "Cron job completed", "results": results}
        except Exception as e:
            logger.error(f"Cron job failed: {e}")
            return {"status": "error", "message": str(e)}

proactive_engine = ProactiveEngine()
