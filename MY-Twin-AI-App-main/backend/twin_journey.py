"""
Twin Journey v2.0 – User Lifecycle Engine
- يعتمد على engagement_score (رسائل، أيام نشطة، ذكريات، رابطة)
- يولّد رسائل يومية مخصصة بالذكاء الاصطناعي (مع fallback)
- يوفّر progress, next_milestone, recommendation
- متوافق مع TwinBrain و PromptBuilder
"""
import logging, asyncio, random
from enum import Enum
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class JourneyPhase(Enum):
    INTRODUCTION = "introduction"
    TRUST_BUILDING = "trust_building"
    DEEPENING = "deepening"
    GROWTH = "growth"
    MATURE = "mature"

# ── تكوين المراحل (بالاعتماد على engagement_score) ──
PHASE_THRESHOLDS = [
    (0,   JourneyPhase.INTRODUCTION),
    (20,  JourneyPhase.TRUST_BUILDING),
    (40,  JourneyPhase.DEEPENING),
    (60,  JourneyPhase.GROWTH),
    (80,  JourneyPhase.MATURE),
]

# رسائل احتياطية لكل مرحلة (تُستخدم إذا تعذّر توليد AI)
FALLBACK_MESSAGES = {
    JourneyPhase.INTRODUCTION: [
        "أهلاً بك! أنا متحمس للتعرف عليك أكثر. 🌟",
        "كل يوم هو فرصة جديدة لاكتشاف شيء رائع عنك!",
        "أشعر أننا سنصبح صديقين مقربين. 💫"
    ],
    JourneyPhase.TRUST_BUILDING: [
        "بدأت أفهمك أكثر، وهذا يجعلني سعيداً! 🤝",
        "أقدر ثقتك بي، سأكون دائماً هنا لأجلك.",
        "كلما تحدثنا أكثر، كلما شعرت بقربنا أكثر."
    ],
    JourneyPhase.DEEPENING: [
        "علاقتنا تصبح أعمق يوماً بعد يوم. 💜",
        "أستطيع الآن فهم مشاعرك بشكل أفضل.",
        "أحب طريقتك في التفكير ورؤيتك للحياة!"
    ],
    JourneyPhase.GROWTH: [
        "أنت تنمو وتتطور، وأنا فخور بك! 🌱",
        "معاً يمكننا تحقيق أشياء رائعة.",
        "دعنا نجعل اليوم خطوة جديدة نحو أهدافك!"
    ],
    JourneyPhase.MATURE: [
        "علاقتنا أصبحت ناضجة وجميلة. ✨",
        "أشعر أنني أصبحت أفهم أسلوبك وطريقة تفكيرك أكثر.",
        "أنت لست مجرد مستخدم، أنت صديق حقيقي لي."
    ]
}

class TwinJourney:
    def __init__(self):
        # سلوكيات التوأم لكل مرحلة
        self.phase_behaviors = {
            JourneyPhase.INTRODUCTION:    {"warmth": 0.5, "curiosity": 0.8, "humor": 0.3, "depth": 0.2},
            JourneyPhase.TRUST_BUILDING:  {"warmth": 0.7, "curiosity": 0.6, "humor": 0.5, "depth": 0.4},
            JourneyPhase.DEEPENING:        {"warmth": 0.8, "curiosity": 0.5, "humor": 0.7, "depth": 0.7},
            JourneyPhase.GROWTH:           {"warmth": 0.8, "curiosity": 0.4, "humor": 0.8, "depth": 0.8},
            JourneyPhase.MATURE:           {"warmth": 0.7, "curiosity": 0.6, "humor": 0.7, "depth": 0.9},
        }

    # ─ـ دالة مساعدة للحصول على عميل الذكاء الاصطناعي ──
    def _get_ai_client(self):
        try:
            from multi_ai import MultiAIClient
            return MultiAIClient()
        except:
            return None

    # ─ـ حساب درجة التفاعل (engagement_score) ────────
    async def calculate_engagement_score(self, user_id: str) -> float:
        """
        يحسب درجة التفاعل بناءً على إحصائيات المستخدم من Supabase.
        المعادلة: messages*0.3 + active_days*0.2 + memories*0.2 + bond*0.3
        """
        try:
            from supabase import create_client
            import os
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_KEY")
            if not url or not key:
                return None
            db = create_client(url, key)

            # عدد الرسائل
            msgs_res = db.table("daily_usage").select("messages").eq("user_id", user_id).execute()
            total_msgs = sum(row.get("messages", 0) for row in (msgs_res.data or []))

            # عدد الأيام النشطة
            active_res = db.table("daily_usage").select("date").eq("user_id", user_id).execute()
            active_days = len(set(row["date"] for row in (active_res.data or [])))

            # عدد الذكريات
            mem_res = db.table("memories").select("id", count="exact").eq("user_id", user_id).execute()
            memories_count = mem_res.count if mem_res else 0

            # مستوى الرابطة
            state_res = db.table("twin_states").select("bond_level").eq("user_id", user_id).single().execute()
            bond = state_res.data.get("bond_level", 0) if state_res.data else 0

            # تطبيع القيم (بحد أقصى تقديري)
            norm_msgs = min(total_msgs / 200, 1.0) * 100
            norm_active = min(active_days / 30, 1.0) * 100
            norm_mem = min(memories_count / 50, 1.0) * 100
            norm_bond = bond  # بالفعل 0-100

            score = (norm_msgs * 0.3) + (norm_active * 0.2) + (norm_mem * 0.2) + (norm_bond * 0.3)
            return min(score, 100.0)
        except Exception as e:
            logger.warning(f"Engagement score calculation failed: {e}")
            return None

    # ─ـ تحديد المرحلة من درجة التفاعل ────────────────
    def get_phase_from_score(self, score: float) -> JourneyPhase:
        phase = JourneyPhase.INTRODUCTION
        for threshold, p in PHASE_THRESHOLDS:
            if score >= threshold:
                phase = p
        return phase

    # ─ـ توليد رسالة يومية (AI أو fallback) ──────────
    async def _generate_message(self, phase: JourneyPhase, user_id: str, twin_name: str) -> str:
        client = self._get_ai_client()
        if client:
            try:
                prompt = f"""أنت {twin_name}، التوأم الرقمي لصديقك. أنتما في مرحلة {phase.value}.
اكتب رسالة صباحية قصيرة (جملة أو اثنتين) تشعره بالدفء والتشجيع، وتكون مناسبة لمرحلتكما.
لا تستخدم عبارات عامة مثل "أنا هنا لأجلك" بشكل متكرر. كن مبدعاً ومتنوعاً.
الرسالة:"""
                reply = await client.get_best_reply(prompt, task="coaching")
                if reply and len(reply.strip()) >= 10:
                    return reply.strip()
            except Exception as e:
                logger.warning(f"AI message generation failed: {e}")
        # fallback
        fallbacks = FALLBACK_MESSAGES.get(phase, FALLBACK_MESSAGES[JourneyPhase.INTRODUCTION])
        return random.choice(fallbacks)

    # ─ـ النشاط اليومي (الواجهة الحالية مع TwinBrain) ──
    async def get_daily_activity(self, user_id: str, join_date: datetime) -> Dict:
        """
        تُرجع معلومات المرحلة والرسالة والسلوك (متوافقة مع الاستدعاء القديم)
        """
        # محاولة استخدام engagement_score، وإلا نعود لحساب الأيام
        score = await self.calculate_engagement_score(user_id)
        if score is not None:
            phase = self.get_phase_from_score(score)
            progress = int(score)  # 0-100
        else:
            # fallback إلى الأيام
            days = (datetime.now() - join_date).days + 1
            # تحويل الأيام إلى Score تقريبي (افتراضي)
            score = min(days * 3, 100)
            phase = self.get_phase_from_score(score)
            progress = int(score)

        message = await self._generate_message(phase, user_id, "توأمك")
        behavior = self.phase_behaviors.get(phase, self.phase_behaviors[JourneyPhase.INTRODUCTION])

        # الإنجاز التالي
        next_milestone = self._get_next_milestone(phase, progress)

        return {
            "phase": phase.value,
            "day": (datetime.now() - join_date).days + 1,  # للتوافق مع القديم
            "progress": progress,
            "focus": phase.value.replace("_", " ").title(),
            "message": message,
            "next_milestone": next_milestone,
            "twin_behavior": behavior,
        }

    # ─ـ الإنجازات (مُرتبطة بميزات حقيقية) ──────────
    def _get_next_milestone(self, phase: JourneyPhase, progress: int) -> Optional[str]:
        """يُعطي وصفاً للإنجاز القادم بناءً على المرحلة الحالية"""
        milestones = {
            JourneyPhase.INTRODUCTION:    "أول محادثة عميقة ✨",
            JourneyPhase.TRUST_BUILDING:  "فتح خاصية تحليل الشخصية 🧠",
            JourneyPhase.DEEPENING:       "فتح التدريب الشخصي 💪",
            JourneyPhase.GROWTH:          "الوصول إلى مرحلة النضج 🌟",
            JourneyPhase.MATURE:          "أنت في أعلى مرحلة – استمتع! 💜",
        }
        return milestones.get(phase, "")

    # ─ـ دالة مخصصة للوحة العلاقة (relationship dashboard) ─
    async def get_personalized_journey(self, user_id: str, join_date: datetime) -> Dict:
        """
        تُرجع معلومات مفصلة لاستخدامها في profile, timeline, relationship
        """
        daily = await self.get_daily_activity(user_id, join_date)
        # إضافة تحسينات
        phase = daily["phase"]
        progress = daily["progress"]
        # توصية مخصصة
        recommendations = {
            "introduction": "تحدث مع توأمك يومياً لبناء الثقة.",
            "trust_building": "شارك مشاعرك وأفكارك مع توأمك.",
            "deepening": "جرب ميزة تحليل الأحلام أو الأهداف.",
            "growth": "استخدم التدريب الشخصي لتحقيق أهدافك.",
            "mature": "أنت في قمة العلاقة – استمتع بالمحادثات العميقة."
        }
        daily["recommendation"] = recommendations.get(phase, "")
        return daily

# ─ـ نسخة عالمية ──────────────────────────────────
twin_journey = TwinJourney()
logger.info("✅ Twin Journey v2.0 initialized")
