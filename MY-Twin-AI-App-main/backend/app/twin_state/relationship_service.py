"""Relationship Service – How am I with you? Bond, dimensions, stages."""
import logging
from typing import Dict, Any, Optional, Tuple
from app.models.relationship import RelationshipState, RelationshipDims, Intent
from app.repositories.relationship_repository import get_state, save_state, log_interaction

logger = logging.getLogger("relationship_service")

RELATIONSHIP_DIMS = {
    "trust": {"label_ar": "ثقة", "label_en": "Trust"},
    "comfort": {"label_ar": "راحة", "label_en": "Comfort"},
    "openness": {"label_ar": "انفتاح", "label_en": "Openness"},
    "attachment": {"label_ar": "ارتباط", "label_en": "Attachment"},
    "romantic": {"label_ar": "عاطفي", "label_en": "Romantic"},
    "humor": {"label_ar": "فكاهة", "label_en": "Humor"},
    "consistency": {"label_ar": "اتساق", "label_en": "Consistency"},
    "shared_history": {"label_ar": "تاريخ مشترك", "label_en": "Shared History"},
    "att_style": {"label_ar": "نمط تعلق", "label_en": "Attachment Style"},
}

STAGES = {
    "stranger":          {"min": 0,  "max": 20,  "label_ar": "غريب",       "label_en": "Stranger"},
    "familiar":          {"min": 20, "max": 40,  "label_ar": "مألوف",       "label_en": "Familiar"},
    "friend":            {"min": 40, "max": 60,  "label_ar": "صديق",        "label_en": "Friend"},
    "close_friend":      {"min": 60, "max": 80,  "label_ar": "صديق مقرب",   "label_en": "Close Friend"},
    "trusted_companion": {"min": 80, "max": 95,  "label_ar": "رفيق موثوق",  "label_en": "Trusted Companion"},
    "soul_twin":         {"min": 95, "max": 100, "label_ar": "توأم روح",    "label_en": "Soul Twin"},
}

STAGE_UP_MESSAGES = {
    "familiar":          {"ar": "بقينا مألوفين لبعض! 💜", "en": "We've become familiar! 💜"},
    "friend":            {"ar": "أنت بقيت صديقي! 🤝",    "en": "You're my friend now! 🤝"},
    "close_friend":      {"ar": "صرنا أصحاب مقربين 💕",   "en": "Close friends now 💕"},
    "trusted_companion": {"ar": "بقيت رفيق موثوق 🏅",    "en": "Trusted companion 🏅"},
    "soul_twin":         {"ar": "إحنا توأم روح! 🌟",     "en": "We're soul twins! 🌟"},
}

EMOTION_EFFECTS = {
    "joy":      {"comfort": 0.2, "humor": 0.3, "openness": 0.1},
    "sadness":  {"openness": 0.3, "trust": 0.2, "attachment": 0.2},
    "fear":     {"attachment": 0.3, "trust": 0.2},
    "anger":    {"openness": 0.1, "trust": -0.1},
    "love":     {"romantic": 0.4, "attachment": 0.3, "trust": 0.2},
    "surprise": {"openness": 0.2, "humor": 0.2},
}

BOND_WEIGHTS = {"trust": 0.25, "comfort": 0.20, "openness": 0.20, "attachment": 0.15, "consistency": 0.10, "shared_history": 0.10}

QUICK_INTENT = {
    "ar": {
        "greeting": ["مرحبا","اهلا","صباح الخير","هاي"],
        "gratitude": ["شكرا","تسلم","ممنون"],
        "goodbye": ["مع السلامة","باي","سلام"],
        "self_reflection": ["أنا مش قادر","عندي مشكلة","محتار","خايف"],
        "goal_setting": ["هدف","أخطط","نفسي أحقق"],
    }
}


def _calc_bond(dims: RelationshipDims) -> float:
    return round(sum(getattr(dims, d, 0.0) * w for d, w in BOND_WEIGHTS.items()), 1)


def _get_stage(bond: float) -> str:
    for stage, info in STAGES.items():
        if info["min"] <= bond < info["max"]:
            return stage
    return "soul_twin"


async def load(user_id: str) -> RelationshipState:
    return await get_state(user_id)


async def update(user_id: str, emotion: Optional[Dict] = None, message: Optional[str] = None,
                 journey_phase: Optional[str] = None, attachment_style: Optional[str] = None,
                 memory_importance: float = 0.5) -> Optional[Dict[str, str]]:
    state = await load(user_id)
    old_stage = state.stage
    dims = state.dims

    if emotion:
        primary = emotion.get("primary", "neutral")
        intensity = emotion.get("intensity", 0.5)
        for dim, change in EMOTION_EFFECTS.get(primary, {}).items():
            val = max(0.0, min(100.0, getattr(dims, dim, 0.0) + change * intensity * 20))
            setattr(dims, dim, val)

    if message:
        detected = _detect_from_message(message)
        for dim, val in detected.items():
            old = getattr(dims, dim, 0.0)
            setattr(dims, dim, max(0.0, min(100.0, old + val * 3)))

    if journey_phase:
        caps = {"introduction":30,"trust_building":60,"deepening":80,"growth":90,"mature":100}
        cap = caps.get(journey_phase, 100)
        for d in dims.model_fields:
            if getattr(dims, d, 0) > cap:
                setattr(dims, d, float(cap))

    if attachment_style:
        style_vals = {"secure":80,"anxious":30,"avoidant":20,"disorganized":10,"unknown":50}
        dims.att_style = dims.att_style * 0.8 + style_vals.get(attachment_style, 50) * 0.2

    dims.consistency = min(100.0, dims.consistency + 0.5)
    if memory_importance > 0.6:
        dims.shared_history = min(100.0, dims.shared_history + 0.5)

    state.bond_level = _calc_bond(dims)
    state.stage = _get_stage(state.bond_level)
    state.interaction_count += 1
    state.relationship_health = min(100.0, state.relationship_health + 0.5)

    await save_state(state)
    await log_interaction(user_id, message or "", emotion.get("primary","neutral") if emotion else "neutral")

    if state.stage != old_stage and state.stage in STAGE_UP_MESSAGES:
        logger.info(f"🎉 Stage Up: {old_stage} → {state.stage}")
        return STAGE_UP_MESSAGES[state.stage]
    return None


def detect_intent(message: str, lang: str = "ar") -> Tuple[str, float]:
    if not message:
        return "general", 0.0
    text = message.lower().strip()
    rules = QUICK_INTENT.get(lang, QUICK_INTENT["ar"])
    best, best_score = "general", 0.0
    for intent, keywords in rules.items():
        score = sum(1.0 / len(keywords) for kw in keywords if kw in text)
        if score > best_score:
            best_score = min(score, 1.0)
            best = intent
    return best, best_score


def _detect_from_message(text: str) -> Dict[str, float]:
    detected = {}
    rules = {
        "trust": ["أثق بك","شكراً لوجودك","trust you"],
        "humor": ["ههه","😂","نكتة","lol","funny"],
        "romantic": ["أحبك","حبيبي","قلبي","love you"],
        "openness": ["أنا مش قادر","خايف أقول","عندي مشكلة"],
        "comfort": ["برتاح معاك","أنت فاهم"],
        "attachment": ["بحتاجك","ما تغيبش","need you"],
    }
    for dim, phrases in rules.items():
        for phrase in phrases:
            if phrase in text.lower():
                detected[dim] = detected.get(dim, 0) + 0.1
    return detected
