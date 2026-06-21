"""
Journey Service v2.0 – رحلة المستخدم (متكامل مع TCMA)
=========================================================
- تحديد المرحلة من مستوى الثقة في TCMA
- سلوكيات مخصصة لكل مرحلة
- رسائل يومية وتوصيات
"""
import logging, random
from typing import Dict, Optional

logger = logging.getLogger("journey_service")

try:
    from app.memory.relationship.relationship_memory import get_relationship_insights
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

PHASE_THRESHOLDS = [(0,"introduction"),(20,"trust_building"),(40,"deepening"),(60,"growth"),(80,"mature")]

FALLBACK_MESSAGES = {
    "introduction": ["أهلاً بك! متحمس للتعرف عليك. 🌟","كل يوم فرصة جديدة!"],
    "trust_building": ["بدأت أفهمك أكثر! 🤝","أقدر ثقتك بي."],
    "deepening": ["علاقتنا تصبح أعمق. 💜","أفهم مشاعرك أفضل."],
    "growth": ["أنت تنمو وأنا فخور! 🌱","معاً نحقق أشياء رائعة."],
    "mature": ["علاقتنا ناضجة وجميلة. ✨","أنت صديق حقيقي."],
}

PHASE_BEHAVIORS = {
    "introduction":   {"warmth":0.5,"curiosity":0.8,"humor":0.3,"depth":0.2},
    "trust_building": {"warmth":0.7,"curiosity":0.6,"humor":0.5,"depth":0.4},
    "deepening":      {"warmth":0.8,"curiosity":0.5,"humor":0.7,"depth":0.7},
    "growth":         {"warmth":0.8,"curiosity":0.4,"humor":0.8,"depth":0.8},
    "mature":         {"warmth":0.7,"curiosity":0.6,"humor":0.7,"depth":0.9},
}

def get_phase(score: float) -> str:
    phase = "introduction"
    for threshold, p in PHASE_THRESHOLDS:
        if score >= threshold:
            phase = p
    return phase

async def get_current_phase(user_id: str) -> str:
    """تحديد المرحلة الحالية من TCMA"""
    if TCMA_AVAILABLE:
        try:
            rel = await get_relationship_insights(user_id)
            trust = rel.get("trust_level", 0) if rel else 0
            return get_phase(trust)
        except Exception as e:
            logger.warning(f"TCMA phase failed: {e}")
    return "introduction"

def get_behavior(phase: str) -> Dict:
    return PHASE_BEHAVIORS.get(phase, PHASE_BEHAVIORS["introduction"])

def get_daily_message(phase: str, lang: str = "ar") -> str:
    return random.choice(FALLBACK_MESSAGES.get(phase, FALLBACK_MESSAGES["introduction"]))

async def get_recommendation(user_id: str, lang: str = "ar") -> str:
    """توصية مخصصة بناءً على مرحلة المستخدم"""
    phase = await get_current_phase(user_id)
    recommendations = {
        "introduction": "تحدث مع توأمك يومياً لبناء علاقتكما.",
        "trust_building": "شارك توأمك بشيء شخصي لتعميق ثقتكما.",
        "deepening": "جرب تحليل الأحلام أو جلسة تدريب حياة.",
        "growth": "استخدم ميزات الدراسة أو الأعمال لتحقيق أهدافك.",
        "mature": "علاقتكما قوية. استمر في النمو معاً.",
    }
    return recommendations.get(phase, recommendations["introduction"])

logger.info("✅ Journey Service v2.0 initialized")
