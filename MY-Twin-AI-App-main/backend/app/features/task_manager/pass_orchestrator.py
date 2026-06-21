"""
PASS Orchestrator – عقل إدارة المهام الذكية
=============================================
يدير: المهام، التقويم، الإيميلات، والتذكيرات.
يتكامل مع TCMA لتذكر عادات المستخدم والتزاماته.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory
    from app.memory.reflection.reflection_engine import store_reflection
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger("pass_orchestrator")

class PASSOrchestrator:
    def __init__(self):
        self.tasks: Dict[str, List[Dict]] = {}
        self.calendar_events: Dict[str, List[Dict]] = {}

    # ========== إدارة المهام ==========
    async def create_task(
        self, user_id: str, title: str, due_date: str = "", priority: str = "medium",
        category: str = "personal", notes: str = ""
    ) -> Dict[str, Any]:
        task = {
            "id": f"task_{len(self.tasks.get(user_id, [])) + 1}",
            "title": title,
            "due_date": due_date or (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "priority": priority,
            "category": category,
            "notes": notes,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if user_id not in self.tasks:
            self.tasks[user_id] = []
        self.tasks[user_id].append(task)

        # تخزين في TCMA
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=f"مهمة جديدة: {title}",
                detected_emotion={"primary": "focused", "intensity": 0.6, "valence": 0.2},
                trigger="task_created", cultural_context=f"فئة: {category}"
            )

        # تخزين في قاعدة البيانات إن وجدت
        if DB_AVAILABLE:
            try:
                db = get_db()
                db.table("tasks").insert({
                    "user_id": user_id, "title": title,
                    "due_date": task["due_date"], "priority": priority,
                    "category": category, "notes": notes, "status": "pending"
                }).execute()
            except: pass

        return {"task": task, "message": f"✅ تم إنشاء المهمة: {title}"}

    async def list_tasks(self, user_id: str, status: str = "all") -> List[Dict]:
        tasks = self.tasks.get(user_id, [])
        if status != "all":
            tasks = [t for t in tasks if t.get("status") == status]

        # إضافة سياق من TCMA
        context = ""
        if TCMA_AVAILABLE:
            try:
                from app.memory.emotional.emotional_memory import get_emotional_patterns
                patterns = await get_emotional_patterns(user_id, days=7)
                context = patterns.get("dominant_emotion", "neutral")
            except: pass

        return {"tasks": tasks, "total": len(tasks), "user_emotion": context}

    async def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        tasks = self.tasks.get(user_id, [])
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now(timezone.utc).isoformat()
                
                # تخزين في TCMA
                if TCMA_AVAILABLE:
                    await store_emotional_memory(
                        user_id=user_id, expressed_text=f"أكملت مهمة: {task['title']}",
                        detected_emotion={"primary": "joy", "intensity": 0.8, "valence": 0.7},
                        trigger="task_completed"
                    )
                    await store_reflection(
                        user_id=user_id, insight_type="productivity",
                        insight_text=f"أنجز مهمة: {task['title']}", confidence=0.8
                    )
                return {"task": task, "message": f"🎉 تم إنجاز: {task['title']}"}
        return {"error": "المهمة غير موجودة"}

    # ========== التقويم والمواعيد ==========
    async def add_calendar_event(
        self, user_id: str, title: str, event_date: str, event_time: str = "",
        event_type: str = "meeting", location: str = ""
    ) -> Dict[str, Any]:
        event = {
            "id": f"event_{len(self.calendar_events.get(user_id, [])) + 1}",
            "title": title,
            "date": event_date,
            "time": event_time,
            "type": event_type,
            "location": location,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if user_id not in self.calendar_events:
            self.calendar_events[user_id] = []
        self.calendar_events[user_id].append(event)

        # حساب التذكير
        reminder_date = datetime.fromisoformat(event_date) - timedelta(hours=2)

        return {
            "event": event,
            "reminder": f"⏰ سيتم تذكيرك قبل الموعد بساعتين: {reminder_date.strftime('%Y-%m-%d %H:%M')}"
        }

    async def get_upcoming_events(self, user_id: str, days: int = 7) -> List[Dict]:
        events = self.calendar_events.get(user_id, [])
        now = datetime.now(timezone.utc)
        upcoming = []
        for e in events:
            event_dt = datetime.fromisoformat(e["date"])
            if event_dt >= now and event_dt <= now + timedelta(days=days):
                upcoming.append(e)
        return {"events": upcoming, "days": days}

    # ========== المناسبات والتذكيرات ==========
    async def add_reminder(
        self, user_id: str, title: str, reminder_date: str, repeat: str = "none"
    ) -> Dict[str, Any]:
        # يمكن تخزينها كمهمة مع خاصية التكرار
        return await self.create_task(
            user_id=user_id, title=f"🔔 {title}",
            due_date=reminder_date, priority="high", category="reminder"
        )

    # ========== الإيميلات ==========
    async def compose_email(
        self, user_id: str, to: str, subject: str, body: str
    ) -> Dict[str, Any]:
        # في النسخة الإنتاجية: سنستخدم SendGrid أو SMTP
        return {
            "draft": {"to": to, "subject": subject, "body": body},
            "message": "📧 تم تحضير المسودة. سأرسلها عند تفعيل خدمة الإيميل."
        }


# نسخة عالمية
pass_assistant = PASSOrchestrator()
logger.info("✅ P.A.S.S. Orchestrator initialized")

    # ========== خدمات خارجية ==========
    async def get_dashboard(self, user_id: str) -> Dict[str, Any]:
        """لوحة معلومات شاملة: مهام + طقس + أخبار + عملات"""
        from app.features.task_manager.external_services import get_weather, get_news, get_currency
        
        tasks = await self.list_tasks(user_id)
        weather = await get_weather("Cairo")
        news = await get_news("sa")
        currency = await get_currency("USD", "SAR,EGP,EUR")

        return {
            "tasks": tasks.get("tasks", []),
            "weather": weather,
            "news": news.get("articles", []),
            "currency": currency.get("rates", {}),
            "user_emotion": tasks.get("user_emotion", "neutral"),
            "recommendation": self._generate_recommendation(weather, tasks)
        }

    def _generate_recommendation(self, weather: Dict, tasks: Dict) -> str:
        """توليد توصية مخصصة بناءً على الطقس والمهام"""
        if isinstance(weather, dict) and "temperature" in weather:
            temp = float(weather["temperature"])
            if temp > 35:
                return "الجو حار جداً. احرص على شرب الماء ولا تنسَ مهامك!"
            elif temp < 10:
                return "الجو بارد. ارتدِ ملابس دافئة أثناء إنجاز مهامك."
        return "يوم جيد لإنجاز مهامك!"

pass_assistant = PASSOrchestrator()

    async def get_google_calendar_events(self, user_id: str) -> Dict[str, Any]:
        """جلب أحداث Google Calendar"""
        if not DB_AVAILABLE:
            return {"events": [], "connected": False}
        try:
            import httpx
            db = get_db()
            profile = db.table("profiles").select("calendar_token").eq("id", user_id).single().execute()
            if not profile.data or not profile.data.get("calendar_token"):
                return {"events": [], "connected": False}
            
            token = profile.data["calendar_token"]
            now = datetime.now(timezone.utc).isoformat()
            end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"timeMin": now, "timeMax": end, "maxResults": 10, "singleEvents": True, "orderBy": "startTime"},
                    timeout=10.0
                )
                if resp.status_code == 200:
                    events = resp.json().get("items", [])
                    return {
                        "events": [{"id": e["id"], "title": e.get("summary",""), "start": e.get("start",{}).get("dateTime",""), "type": "google"} for e in events],
                        "connected": True
                    }
        except Exception as e:
            logger.error(f"Google Calendar failed: {e}")
        return {"events": [], "connected": False}

pass_assistant = PASSOrchestrator()
