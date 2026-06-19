"""Journey Service – phase, progress, behaviors, messages (AR + EN)."""
import logging, random
from typing import Dict
from app.core.i18n import msg

logger = logging.getLogger("journey_service")

PHASES = [(0,"introduction"),(20,"trust_building"),(40,"deepening"),(60,"growth"),(80,"mature")]

BEHAVIORS = {
    "introduction":   {"warmth":0.5,"curiosity":0.8,"humor":0.3,"depth":0.2},
    "trust_building": {"warmth":0.7,"curiosity":0.6,"humor":0.5,"depth":0.4},
    "deepening":      {"warmth":0.8,"curiosity":0.5,"humor":0.7,"depth":0.7},
    "growth":         {"warmth":0.8,"curiosity":0.4,"humor":0.8,"depth":0.8},
    "mature":         {"warmth":0.7,"curiosity":0.6,"humor":0.7,"depth":0.9},
}

FALLBACK_MESSAGES = {
    "introduction":   ["greeting_intro", "greeting_new_day"],
    "trust_building": ["trust_growing", "trust_appreciate"],
    "deepening":      ["deepening_close", "deepening_understand"],
    "growth":         ["growth_proud", "growth_together"],
    "mature":         ["mature_beautiful", "mature_friend"],
}

RECOMMENDATION_KEYS = {
    "introduction": "recommendation_intro",
    "trust_building": "recommendation_trust",
    "deepening": "recommendation_deepen",
    "growth": "recommendation_growth",
    "mature": "recommendation_mature",
}


async def get_phase(score: float) -> str:
    phase = "introduction"
    for threshold, p in PHASES:
        if score >= threshold: phase = p
    return phase

async def get_behavior(phase: str) -> Dict:
    return BEHAVIORS.get(phase, BEHAVIORS["introduction"])

async def get_daily_message(phase: str, lang: str = "ar") -> str:
    keys = FALLBACK_MESSAGES.get(phase, FALLBACK_MESSAGES["introduction"])
    key = random.choice(keys)
    return msg(key, lang)

async def get_recommendation(phase: str, lang: str = "ar") -> str:
    key = RECOMMENDATION_KEYS.get(phase, "recommendation_intro")
    return msg(key, lang)

async def calculate_score(total_messages: int, active_days: int,
                          memory_count: int, bond_level: float) -> float:
    norm_msgs = min(total_messages / 200, 1.0) * 100
    norm_days = min(active_days / 30, 1.0) * 100
    norm_mem = min(memory_count / 50, 1.0) * 100
    return min(norm_msgs * 0.3 + norm_days * 0.2 + norm_mem * 0.2 + bond_level * 0.3, 100.0)
