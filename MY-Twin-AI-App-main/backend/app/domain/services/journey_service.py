"""Journey Service – user lifecycle, engagement score, daily messages."""
import logging, random
from typing import Dict

logger = logging.getLogger("journey_service")

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

def get_behavior(phase: str) -> Dict:
    return PHASE_BEHAVIORS.get(phase, PHASE_BEHAVIORS["introduction"])

def get_daily_message(phase: str) -> str:
    return random.choice(FALLBACK_MESSAGES.get(phase, FALLBACK_MESSAGES["introduction"]))
