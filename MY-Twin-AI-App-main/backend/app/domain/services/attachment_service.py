"""
Attachment Service v3.0 – كشف نمط التعلق (متكامل مع TCMA)
=============================================================
- يفضل TCMA Attachment Model إذا كان متاحاً
- يعود للمنطق المحلي (الكلمات المفتاحية) كاحتياط
- يستخدم في Twin State و Life Coach
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("attachment_service")

try:
    from app.memory.relationship.attachment_model import detect_attachment_style as tcma_detect
    TCMA_ATTACHMENT_AVAILABLE = True
except ImportError:
    TCMA_ATTACHMENT_AVAILABLE = False

INDICATORS = {
    "secure":       {"words": ["أثق بك","أشعر بالراحة","شكراً لوجودك"], "emotions": ["joy","love","calm"]},
    "anxious":      {"words": ["هل تحبني","أفتقدك","لماذا تأخرت","رد علي"], "emotions": ["fear","sadness"]},
    "avoidant":     {"words": ["لا أحتاج أحداً","أفضل وحدتي","ما لي خلق"], "emotions": ["neutral","calm"]},
    "disorganized": {"words": ["لا أعرف ما أشعر به","أحتاجك لكن أخاف"], "emotions": ["fear","love"]},
}

RESPONSE_ADJUSTMENTS = {
    "secure":       {"warmth":0.7,"challenge":0.6,"support":"growth_focused","humor":0.6,"tone":"balanced"},
    "anxious":      {"warmth":0.9,"challenge":0.3,"support":"reassurance","humor":0.4,"tone":"soothing"},
    "avoidant":     {"warmth":0.4,"challenge":0.2,"support":"respectful_distance","humor":0.3,"tone":"gentle"},
    "disorganized": {"warmth":0.8,"challenge":0.1,"support":"stable_presence","humor":0.2,"tone":"safe"},
    "unknown":      {"warmth":0.6,"challenge":0.4,"support":"exploratory","humor":0.5,"tone":"neutral"},
}

async def detect_style(messages: List[str] = None, user_id: str = None, emotion_history: Optional[List[Dict]] = None) -> Dict:
    """يكتشف نمط التعلق. يفضل TCMA إذا كان user_id متاحاً."""
    if TCMA_ATTACHMENT_AVAILABLE and user_id:
        try:
            result = await tcma_detect(user_id)
            if result and result.get("style") and result["style"] != "unknown":
                return result
        except Exception as e:
            logger.warning(f"TCMA attachment failed: {e}")

    if not messages:
        return {"style":"unknown","confidence":0.0}
    recent = messages[-20:]
    scores = {"secure":0,"anxious":0,"avoidant":0,"disorganized":0}
    for msg in recent:
        for style, indicators in INDICATORS.items():
            for word in indicators["words"]:
                if word in msg:
                    scores[style] += 1
        if emotion_history:
            for emo in emotion_history[-10:]:
                for style, indicators in INDICATORS.items():
                    if emo.get("primary") in indicators["emotions"]:
                        scores[style] += 0.5
        if _has_anxiety(msg): scores["anxious"] += 1; scores["disorganized"] += 0.5
        if _has_avoidance(msg): scores["avoidant"] += 1
        if _has_contradiction(msg): scores["disorganized"] += 1
        if _has_secure(msg): scores["secure"] += 1
    total = sum(scores.values())
    if total == 0: return {"style":"unknown","confidence":0.0}
    dominant = max(scores, key=scores.get)
    return {"style":dominant,"confidence":min(scores[dominant]/total,1.0)}

def get_adjustments(style: str) -> Dict:
    return RESPONSE_ADJUSTMENTS.get(style, RESPONSE_ADJUSTMENTS["unknown"])

def _has_anxiety(msg): return any(w in msg for w in ["خائف","قلق","متوتر","هل تحبني","لا تتركني","أحتاجك","وينك","بسرعة","رد علي"])
def _has_avoidance(msg): return any(w in msg for w in ["لا أريد التحدث","لست بحاجة","أفضل وحدي","خليني","ما لي خلق"])
def _has_contradiction(msg): return any(w in msg for w in ["أحتاجك","تعال"]) and any(w in msg for w in ["لكن لا","ابتعد","ما أقدر"])
def _has_secure(msg): return any(w in msg for w in ["شكراً","فهمتني","أنت الأفضل","أنا مرتاح"])

logger.info("✅ Attachment Service v3.0 initialized (TCMA Integrated)")
