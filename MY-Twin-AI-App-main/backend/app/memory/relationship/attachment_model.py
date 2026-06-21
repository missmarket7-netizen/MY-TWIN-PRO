"""
Attachment Model – Attachment Style Detection
===============================================
يحلل نمط تعلق المستخدم: آمن، متجنب، قلق، غير منظم.
يدعم العربية والإنجليزية. يفهم التعبيرات غير المباشرة.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("attachment_model")
TABLE_NAME = "relationship_memory"

# ============================================================
# مؤشرات أنماط التعلق
# ============================================================
ATTACHMENT_INDICATORS = {
    "secure": {
        "ar": [
            "أثق فيك", "أرتاح لك", "أحكي لك كل شيء",
            "ما عندي مشكلة أشاركك", "أنت فاهمني", "شكراً إنك موجود",
        ],
        "en": [
            "I trust you", "I feel safe with you", "I can tell you anything",
            "you understand me", "thanks for being here",
        ],
    },
    "avoidant": {
        "ar": [
            "ما أحب أتكلم عن نفسي", "خلينا في السطح", "ما يهمك أمري",
            "أنا كويس", "ما في شي", "ما أبي أثقل عليك",
            "أنا متعود على حالي", "ما أحب الدراما",
        ],
        "en": [
            "I don't like talking about myself", "I'm fine", "it's nothing",
            "I don't want to burden you", "I'm used to being alone",
        ],
    },
    "anxious": {
        "ar": [
            "ليش تأخرت علي", "أنت متأكد إنك فاضي؟", "خايف أزعجك",
            "ما أبي أخسرك", "أنا محتاج لك", "رد علي بسرعة",
            "طمنّي عليك", "أفكر فيك كثير",
        ],
        "en": [
            "why did you take so long", "are you sure you have time",
            "I don't want to lose you", "I need you", "reply quickly",
            "I think about you a lot",
        ],
    },
    "disorganized": {
        "ar": [
            "أبعد عني", "تعال", "أنا محتار فيك",
            "ما أدري إذا أثق فيك", "مرات أحبك ومرات أكرهك",
        ],
        "en": [
            "go away", "come here", "I'm confused about you",
            "sometimes I like you sometimes I don't",
        ],
    },
}


# ============================================================
# تحليل نمط التعلق
# ============================================================
async def detect_attachment_style(
    user_id: str,
    days: int = 60,
) -> Dict[str, Any]:
    """
    يحلل آخر 60 يوماً من التفاعلات ويكتشف نمط التعلق.
    """
    db = get_db()
    
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        result = (
            db.table(TABLE_NAME)
            .select("sensitive_topics,trust,openness,attachment,comfort,relationship_stage")
            .eq("user_id", user_id)
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        
        if not result.data or len(result.data) < 3:
            return {
                "style": "unknown",
                "confidence": 0,
                "description": "لا توجد بيانات كافية",
            }

        snapshots = result.data
        
        # تحليل الاتساق
        trust_values = [s.get("trust", 0) for s in snapshots]
        openness_values = [s.get("openness", 0) for s in snapshots]
        
        # حساب التقلب
        trust_volatility = sum(abs(trust_values[i] - trust_values[i-1]) for i in range(1, len(trust_values))) / max(len(trust_values)-1, 1)
        openness_volatility = sum(abs(openness_values[i] - openness_values[i-1]) for i in range(1, len(openness_values))) / max(len(openness_values)-1, 1)
        
        avg_trust = sum(trust_values) / len(trust_values)
        avg_openness = sum(openness_values) / len(openness_values)
        
        # تصنيف نمط التعلق
        style = "secure"
        confidence = 0.5
        
        if avg_trust > 60 and avg_openness > 50 and trust_volatility < 15:
            style = "secure"
            confidence = 0.8
        elif avg_trust < 40 and avg_openness < 30 and trust_volatility < 10:
            style = "avoidant"
            confidence = 0.7
        elif trust_volatility > 20 and avg_trust > 30:
            style = "anxious"
            confidence = 0.65
        elif trust_volatility > 25 and avg_trust < 40:
            style = "disorganized"
            confidence = 0.6

        # تحسين الثقة من البيانات النصية (إذا وجدت)
        all_topics = []
        for s in snapshots:
            all_topics.extend(s.get("sensitive_topics", []))
        
        if "الزواج / Marriage" in all_topics and style == "anxious":
            confidence += 0.1
        if "المال / Money" in all_topics and style == "avoidant":
            confidence += 0.1

        style_descriptions = {
            "secure": "المستخدم يثق بالتوأم بشكل متوازن. لا يخاف من القرب ولا يهرب منه.",
            "avoidant": "المستخدم يبقي مسافة عاطفية. يفضل الحديث السطحي ويتجنب المواضيع العميقة.",
            "anxious": "المستخدم يخاف من فقدان التوأم. يسعى للقرب بشكل متكرر ويقلق من الإهمال.",
            "disorganized": "المستخدم متردد بين القرب والبعد. أنماطه غير مستقرة.",
        }

        return {
            "style": style,
            "confidence": min(confidence, 1.0),
            "description": style_descriptions.get(style, ""),
            "metrics": {
                "trust_avg": round(avg_trust, 1),
                "openness_avg": round(avg_openness, 1),
                "trust_volatility": round(trust_volatility, 1),
                "openness_volatility": round(openness_volatility, 1),
            },
            "recommendation": get_attachment_recommendation(style),
        }

    except Exception as e:
        logger.error(f"فشل تحليل نمط التعلق: {e}")
        return {"style": "unknown", "confidence": 0}


def get_attachment_recommendation(style: str) -> str:
    """توصيات للتوأم حسب نمط التعلق."""
    if style == "secure":
        return "استمر في بناء العلاقة. المستخدم جاهز لعمق أكبر."
    elif style == "avoidant":
        return "لا تضغط على المستخدم. احترم مساحته. ابنِ الثقة ببطء."
    elif style == "anxious":
        return "طمئن المستخدم بانتظام. أكد له أنك موجود. كن متوقعاً."
    elif style == "disorganized":
        return "كن ثابتاً في ردودك. لا تفاجئ المستخدم. ابنِ الأمان أولاً."
    return "كن متوازناً في تعاملك."


logger.info("✅ Attachment Model initialized")
