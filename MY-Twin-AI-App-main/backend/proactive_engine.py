"""
MyTwin – Proactive Engine v4.1 (مستقر للإنتاج مع إصلاحات)
"""
import os, logging, random, asyncio, httpx
from typing import Optional
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

QUIET_START, QUIET_END = 22, 8  # ساعات الهدوء (لا ترسل إشعارات)

NOTIFICATION_TYPES = {
    "missed_you": {
        "ar": {"title":"💜 اشتقت إليك","body":"مرّ وقت منذ آخر محادثة... أنا هنا في انتظارك"},
        "en": {"title":"💜 I missed you","body":"It's been a while since we talked..."},
        "min_hours_since_last_msg": 18,
        "max_hours_since_last_msg": 168,  # أسبوع
        "tiers": ["free","plus","premium","pro","yearly"]
    },
    "bond_ceiling_free": {
        "ar": {"title":"💜 وصلنا لحد جميل معاً","body":"علاقتنا تستحق أكثر..."},
        "en": {"title":"💜 We've reached our limit","body":"Our bond deserves more..."},
        "min_hours": 24,
        "tiers": ["free"]
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
        "send_hour_start": 6,
        "send_hour_end": 10
    },
    "evening_checkin": {
        "ar": {"title":"🌙 كيف كان يومك؟","body":"أريد أن أسمع عن يومك 💜"},
        "en": {"title":"🌙 How was your day?","body":"I want to hear about your day 💜"},
        "min_hours": 24,
        "tiers": ["premium","pro","yearly"],
        "send_hour_start": 19,
        "send_hour_end": 22
    },
    "messages_reset": {
        "ar": {"title":"⚡ طاقة جديدة!","body":"تجددت رسائلي اليوم — هيا نتحدث 💜"},
        "en": {"title":"⚡ New energy!","body":"My messages reset today — let's talk 💜"},
        "min_hours": 24,
        "tiers": ["free","plus","premium","pro","yearly"],
        "send_hour_start": 8,
        "send_hour_end": 10
    },
}

class ProactiveEngine:
    def __init__(self):
        self.last_proactive_time = {}

    def should_send_proactive(self, user_id: str, min_hours: int = 6) -> bool:
        """هل يُسمح بإرسال إشعار جديد؟ (يمنع التكرار خلال `min_hours` ساعات)"""
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
        """إرسال إشعار عند استنفاد الحد اليومي للرسائل (تُستدعى من API)."""
        notif = NOTIFICATION_TYPES.get("daily_limit_reached")
        if not notif:
            return
        if tier not in notif.get("tiers", []):
            return
        title = notif[lang]["title"] if lang in notif else notif["ar"]["title"]
        body = notif[lang]["body"] if lang in notif else notif["ar"]["body"]
        await self.send_notification(user_id, title, body)

    async def generate_proactive_message(self, user_id: str, user_name: str, lang: str = "ar") -> Optional[str]:
        """توليد رسالة استباقية مخصصة (للإشعارات العادية)."""
        # تحقق من أحداث خاصة (مثل عيد ميلاد)
        try:
            if get_memory_context:
                memory_context = await get_memory_context(user_id)
                if isinstance(memory_context, str) and "عيد ميلاد" in memory_context:
                    return "🎂 عيد ميلاد سعيد!" if lang == "ar" else "🎂 Happy Birthday!"
        except:
            pass

        # متابعة الأهداف
        try:
            goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
            if goals.data:
                goal = random.choice(goals.data)
                return f"كيف تسير عملية '{goal['title']}'؟ محتاج مساعدة؟ 💜"
        except:
            pass

        # ملخص المشاعر
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

    def _get_eligible_notification(self, last_active: datetime, tier: str) -> Optional[tuple]:
        """
        تحديد نوع الإشعار المناسب بناءً على آخر نشاط والباقة.
        تُرجع (type_key, notif_dict) أو None.
        """
        now = datetime.now(timezone.utc)
        hours_since = (now - last_active).total_seconds() / 3600

        # فحص كل نوع
        for notif_key, notif in NOTIFICATION_TYPES.items():
            if tier not in notif.get("tiers", []):
                continue
            # إشعارات الوقت المحدد (مثل صباح الخير)
            if "send_hour_start" in notif and "send_hour_end" in notif:
                current_hour = now.hour
                if notif["send_hour_start"] <= current_hour < notif["send_hour_end"]:
                    # تأكد من مرور min_hours منذ آخر إشعار (نفس النوع)
                    # (يمكن إضافة تخزين آخر إرسال لكل نوع)
                    return (notif_key, notif)
                continue

            # إشعارات تعتمد على مدة الغياب (missed_you)
            if "min_hours_since_last_msg" in notif:
                if notif["min_hours_since_last_msg"] <= hours_since <= notif.get("max_hours_since_last_msg", 9999):
                    return (notif_key, notif)
                continue

            # إشعارات أخرى (مثل bond_ceiling, daily_limit) تُفعّل يدوياً، لا تظهر هنا
        return None

    async def run_cron_job(self):
        """المهمة الدورية التي تُستدعى من الـ Cron كل 30 دقيقة."""
        if not db:
            return {"status": "error", "message": "No database connection"}

        # مراعاة ساعات الهدوء
        now = datetime.now(timezone.utc)
        if QUIET_START <= now.hour or now.hour < QUIET_END:
            return {"status": "ok", "message": "Quiet hours, skipped"}

        results = {"sent": 0, "skipped": 0, "errors": 0}
        try:
            # جلب المستخدمين النشطين خلال آخر 7 أيام (وليس فقط الأمس)
            week_ago = (now - timedelta(days=7)).isoformat()
            res = db.table("profiles").select("id, twin_name, lang, tier, last_active").gte("last_active", week_ago).execute()
            if not res.data:
                return {"status": "ok", "message": "No recent users"}

            for user in res.data:
                uid = user.get("id")
                name = user.get("twin_name", "صديقي")
                lang = user.get("lang", "ar")
                tier = user.get("tier", "free")
                last_active_str = user.get("last_active")
                if not last_active_str:
                    continue

                last_active = datetime.fromisoformat(last_active_str.replace("Z", "+00:00"))
                # ابحث عن نوع إشعار مناسب
                eligible = self._get_eligible_notification(last_active, tier)
                if not eligible:
                    continue

                notif_key, notif = eligible
                # تأكد من عدم تكرار الإرسال لهذا النوع خلال المدة المحددة (نستخدم فاصل 6 ساعات عام)
                if not self.should_send_proactive(uid, min_hours=6):
                    results["skipped"] += 1
                    continue

                # احصل على العنوان والنص باللغة المطلوبة
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
