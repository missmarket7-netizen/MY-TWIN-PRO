"""
Journey Service v2.0 – متكامل مع TCMA
========================================
يستخدم ذاكرة العلاقات والهوية لتتبع رحلة المستخدم.
"""
import logging, random
from typing import Dict

logger = logging.getLogger("journey_service")

try:
    from app.memory.relationship.relationship_memory import get_relationship_insights
    from app.memory.identity.identity_model import get_identity
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

PHASES = [(0,"introduction"),(20,"trust_building"),(40,"deepening"),(60,"growth"),(80,"mature")]

BEHAVIORS = {
    "introduction":   {"warmth":0.5,"curiosity":0.8,"humor":0.3,"depth":0.2},
    "trust_building": {"warmth":0.7,"curiosity":0.6,"humor":0.5,"depth":0.4},
    "deepening":      {"warmth":0.8,"curiosity":0.5,"humor":0.7,"depth":0.7},
    "growth":         {"warmth":0.8,"curiosity":0.4,"humor":0.8,"depth":0.8},
    "mature":         {"warmth":0.7,"curiosity":0.6,"humor":0.7,"depth":0.9},
}

FALLBACK_MESSAGES = {
    "introduction":   ["مرحباً! أنا سعيد بلقائك.", "كيف يمكنني مساعدتك اليوم؟"],
    "trust_building": ["أثق بك أكثر كل يوم.", "سعيد لأنك تشاركني."],
    "deepening":      ["علاقتنا أصبحت أعمق.", "أفهمك أكثر الآن."],
    "growth":         ["أنت تتطور بشكل رائع.", "فخور بك!"],
    "mature":         ["رحلتنا معاً جميلة.", "أنت صديق حقيقي."],
}

async def get_phase(score: float) -> str:
    phase = "introduction"
    for threshold, p in PHASES:
        if score >= threshold: phase = p
    return phase

async def get_current_phase(user_id: str) -> str:
    """تحديد المرحلة الحالية من TCMA"""
    if TCMA_AVAILABLE:
        try:
            rel = await get_relationship_insights(user_id)
            trust = rel.get("trust_level", 0) if rel else 0
            return await get_phase(trust)
        except Exception as e:
            logger.warning(f"TCMA phase failed: {e}")
    return "introduction"

async def get_behavior(phase: str) -> Dict:
    return BEHAVIORS.get(phase, BEHAVIORS["introduction"])

async def get_daily_message(phase: str, lang: str = "ar") -> str:
    pool = FALLBACK_MESSAGES.get(phase, FALLBACK_MESSAGES["introduction"])
    return random.choice(pool)

async def get_recommendation(phase: str, lang: str = "ar") -> str:
    recommendations = {
        "introduction": "جرب التحدث معي يومياً لبناء علاقتنا.",
        "trust_building": "شاركني بشيء شخصي لتعميق ثقتنا.",
        "deepening": "دعنا نتأمل في مشاعرك اليوم.",
        "growth": "حدد هدفاً جديداً هذا الأسبوع.",
        "mature": "أنت في مرحلة متقدمة. استمر!"
    }
    return recommendations.get(phase, recommendations["introduction"])

async def calculate_score(total_messages: int, active_days: int, memory_count: int, bond_level: float) -> float:
    norm_msgs = min(total_messages / 200, 1.0) * 100
    norm_days = min(active_days / 30, 1.0) * 100
    norm_mem = min(memory_count / 50, 1.0) * 100
    return min(norm_msgs * 0.3 + norm_days * 0.2 + norm_mem * 0.2 + bond_level * 0.3, 100.0)

logger.info("✅ Journey Service v2.0 initialized")
