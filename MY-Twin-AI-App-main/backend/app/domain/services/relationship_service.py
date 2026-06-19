"""
Relationship Service – bond growth, dimensions, stages.
Extracted from relationship_engine.py.
"""
import logging
from typing import Dict, Any, Optional, Tuple

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

EMOTION_DIM_EFFECTS = {
    "joy":      {"comfort": 0.2, "humor": 0.3, "openness": 0.1},
    "sadness":  {"openness": 0.3, "trust": 0.2, "attachment": 0.2},
    "fear":     {"attachment": 0.3, "trust": 0.2},
    "anger":    {"openness": 0.1, "trust": -0.1},
    "love":     {"romantic": 0.4, "attachment": 0.3, "trust": 0.2},
    "surprise": {"openness": 0.2, "humor": 0.2},
}

BOND_WEIGHTS = {"trust": 0.25, "comfort": 0.20, "openness": 0.20, "attachment": 0.15, "consistency": 0.10, "shared_history": 0.10}

QUICK_INTENT_RULES = {
    "ar": {
        "greeting": ["مرحبا","اهلا","صباح الخير","مساء الخير","هاي","السلام عليكم"],
        "gratitude": ["شكرا","تسلم","ممنون"],
        "goodbye": ["مع السلامة","باي","سلام"],
        "weather": ["طقس","جو","حرارة","مطر"],
        "self_reflection": ["أنا مش قادر","عندي مشكلة","محتار","خايف","قلقان"],
        "goal_setting": ["هدف","أخطط","نفسي أحقق"],
    },
    "en": {
        "greeting": ["hello","hi","good morning","hey"],
        "gratitude": ["thank you","thanks","appreciate"],
        "goodbye": ["bye","goodbye","see you"],
        "weather": ["weather","temperature","rain"],
        "self_reflection": ["i can't","i have a problem","confused","scared"],
        "goal_setting": ["goal","plan","achieve"],
    },
}

_user_states: Dict[str, Dict[str, Any]] = {}

def _get_state(user_id: str) -> Dict[str, Any]:
    if user_id not in _user_states:
        _user_states[user_id] = {
            "bond_level": 0.0, "stage": "stranger",
            "dims": {d: 0.0 for d in RELATIONSHIP_DIMS},
            "interaction_count": 0, "relationship_health": 100.0,
        }
    return _user_states[user_id]

def calculate_bond(dims: Dict[str, float]) -> float:
    return round(sum(dims.get(d, 0) * w for d, w in BOND_WEIGHTS.items()), 1)

def get_stage(bond_level: float) -> str:
    for stage_key, info in STAGES.items():
        if info["min"] <= bond_level < info["max"]:
            return stage_key
    return "soul_twin"

def get_stage_label(stage: str, lang: str = "ar") -> str:
    return STAGES.get(stage, {}).get(f"label_{lang}", stage)

async def update_relationship(user_id: str, emotion: Optional[Dict] = None, message: Optional[str] = None, journey_phase: Optional[str] = None, attachment_style: Optional[str] = None, memory_importance: float = 0.5) -> Optional[Dict[str, str]]:
    state = _get_state(user_id)
    old_stage = state["stage"]
    dims = state["dims"]

    if emotion:
        primary = emotion.get("primary", "neutral")
        intensity = emotion.get("intensity", 0.5)
        for dim, change in EMOTION_DIM_EFFECTS.get(primary, {}).items():
            if dim in dims:
                dims[dim] = max(0.0, min(100.0, dims[dim] + change * intensity * 20))

    if message:
        detected = _detect_dimensions_from_message(message)
        for dim, val in detected.items():
            if dim in dims:
                dims[dim] = max(0.0, min(100.0, dims[dim] + val * 0.15 * 20))

    if journey_phase:
        caps = {"introduction": 30, "trust_building": 60, "deepening": 80, "growth": 90, "mature": 100}
        cap = caps.get(journey_phase, 100)
        for dim in dims:
            if dims[dim] > cap:
                dims[dim] = cap

    if attachment_style:
        style_values = {"secure": 80, "anxious": 30, "avoidant": 20, "disorganized": 10, "unknown": 50}
        dims["att_style"] = dims.get("att_style", 0) * 0.8 + style_values.get(attachment_style, 50) * 0.2

    dims["consistency"] = min(100.0, dims.get("consistency", 0) + 0.5)
    if memory_importance > 0.6:
        dims["shared_history"] = min(100.0, dims.get("shared_history", 0) + 0.5)

    state["bond_level"] = calculate_bond(dims)
    state["stage"] = get_stage(state["bond_level"])
    state["interaction_count"] += 1

    if emotion and emotion.get("primary") in ("anger","sadness") and emotion.get("intensity",0) > 0.7:
        state["relationship_health"] = max(0, state["relationship_health"] - 2)
    else:
        state["relationship_health"] = min(100.0, state["relationship_health"] + 0.5)

    new_stage = state["stage"]
    if new_stage != old_stage and new_stage in STAGE_UP_MESSAGES:
        logger.info(f"🎉 Stage Up: {old_stage} → {new_stage}")
        return STAGE_UP_MESSAGES[new_stage]
    return None

def detect_intent(message: str, lang: str = "ar") -> Tuple[str, float]:
    if not message:
        return "general", 0.0
    text = message.lower().strip()
    rules = QUICK_INTENT_RULES.get(lang, QUICK_INTENT_RULES["en"])
    best_intent, best_score = "general", 0.0
    for intent, keywords in rules.items():
        score = sum(1.0 / len(keywords) for kw in keywords if kw in text)
        if score > best_score:
            best_score = min(score, 1.0)
            best_intent = intent
    return best_intent, best_score

def _detect_dimensions_from_message(message: str) -> Dict[str, float]:
    text = message.lower()
    detected = {}
    rules = {
        "trust": ["أثق بك","أخبرتك سراً","شكراً لوجودك","trust you"],
        "humor": ["ههه","😂","نكتة","مضحك","lol","funny"],
        "romantic": ["أحبك","حبيبي","قلبي","وحشتني","love you"],
        "openness": ["أنا مش قادر","خايف أقول","عندي مشكلة"],
        "comfort": ["برتاح معاك","أنت فاهم"],
        "attachment": ["بحتاجك","ما تغيبش","need you"],
    }
    for dim, phrases in rules.items():
        for phrase in phrases:
            if phrase in text:
                detected[dim] = detected.get(dim, 0) + 0.1
    return detected
