"""Attachment Service – style detection, response tuning (AR + EN)."""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("attachment_service")

INDICATORS = {
    "secure": {
        "words": [
            "أثق بك","أشعر بالراحة","شكراً لوجودك","أنت تفهمني","براحتك",
            "i trust you","i feel comfortable","thank you for being here","you understand me","feel safe"
        ],
        "emotions": ["joy","love","calm"]
    },
    "anxious": {
        "words": [
            "هل تحبني","أفتقدك","لماذا تأخرت","رد علي","بسرعة","لا تتركني","وينك",
            "do you love me","i miss you","why are you late","reply","don't leave me","where are you"
        ],
        "emotions": ["fear","sadness"]
    },
    "avoidant": {
        "words": [
            "لا أحتاج أحداً","أفضل وحدتي","ما لي خلق","لا يهم","خليني",
            "i don't need anyone","i prefer being alone","not in the mood","doesn't matter","leave me"
        ],
        "emotions": ["neutral","calm"]
    },
    "disorganized": {
        "words": [
            "لا أعرف ما أشعر به","أحتاجك لكن أخاف","تعال لا تبتعد","أبيك بس ما أقدر",
            "i don't know how i feel","i need you but i'm scared","come close don't go","i want you but i can't"
        ],
        "emotions": ["fear","love"]
    },
}

ADJUSTMENTS = {
    "secure":       {"warmth": 0.7, "challenge": 0.6, "support": "growth_focused",   "humor": 0.6, "tone": "balanced"},
    "anxious":      {"warmth": 0.9, "challenge": 0.3, "support": "reassurance",       "humor": 0.4, "tone": "soothing"},
    "avoidant":     {"warmth": 0.4, "challenge": 0.2, "support": "respectful_distance","humor": 0.3, "tone": "gentle"},
    "disorganized": {"warmth": 0.8, "challenge": 0.1, "support": "stable_presence",    "humor": 0.2, "tone": "safe"},
    "unknown":      {"warmth": 0.6, "challenge": 0.4, "support": "exploratory",       "humor": 0.5, "tone": "neutral"},
}


async def detect(messages: List[str], emotion_history: Optional[List[Dict]] = None) -> Dict:
    if not messages:
        return {"style": "unknown", "confidence": 0.0}
    recent = messages[-20:]
    scores = {"secure": 0, "anxious": 0, "avoidant": 0, "disorganized": 0}
    for msg in recent:
        for style, indicators in INDICATORS.items():
            for word in indicators["words"]:
                if word.lower() in msg.lower():
                    scores[style] += 1
        if emotion_history:
            for emo in emotion_history[-10:]:
                for style, ind in INDICATORS.items():
                    if emo.get("primary") in ind["emotions"]:
                        scores[style] += 0.5
        if _anxiety(msg): scores["anxious"] += 1; scores["disorganized"] += 0.5
        if _avoidance(msg): scores["avoidant"] += 1
        if _contradiction(msg): scores["disorganized"] += 1
        if _secure(msg): scores["secure"] += 1
    total = sum(scores.values())
    if total == 0: return {"style": "unknown", "confidence": 0.0}
    dominant = max(scores, key=scores.get)
    return {"style": dominant, "confidence": min(scores[dominant] / total, 1.0)}


async def get_adjustments(style: str) -> Dict:
    return ADJUSTMENTS.get(style, ADJUSTMENTS["unknown"])


def _anxiety(msg):
    m = msg.lower()
    return any(w in m for w in ["خائف","قلق","متوتر","هل تحبني","لا تتركني","أحتاجك","وينك","بسرعة","رد علي",
                                "scared","worried","anxious","do you love me","don't leave","need you","reply fast"])

def _avoidance(msg):
    m = msg.lower()
    return any(w in m for w in ["لا أريد التحدث","لست بحاجة","أفضل وحدي","خليني","ما لي خلق",
                                "don't want to talk","don't need","prefer alone","leave me","not in the mood"])

def _contradiction(msg):
    m = msg.lower()
    approach = any(w in m for w in ["أحتاجك","تعال","أقترب","أبيك","need you","come close","i want you"])
    avoid = any(w in m for w in ["لكن لا","ابتعد","ما أقدر","but no","go away","i can't"])
    return approach and avoid

def _secure(msg):
    m = msg.lower()
    return any(w in m for w in ["شكراً","فهمتني","أنت الأفضل","أنا مرتاح",
                                "thank you","you understand","you're the best","i'm comfortable","feel safe"])
