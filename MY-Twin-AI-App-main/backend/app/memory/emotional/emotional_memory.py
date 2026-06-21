"""
Emotional Memory - Layer 4 of TCMA
محرك عاطفي سياقي متكامل. يفهم التعبيرات العربية غير المباشرة.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from collections import Counter
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("emotional_memory")
TABLE_NAME = "emotional_memory"

# ============================================================
# قاموس التعابير العربية السياقية (6 فئات - 70+ تعبير)
# ============================================================

ARABIC_CONTEXTUAL_PATTERNS = {
    "sadness_disguised": {
        "patterns": [
            "الحمد لله على كل حال", "ربنا يفرجها", "مش مهم",
            "كل شيء قسمة ونصيب", "الدنيا وما فيها", "خير إن شاء الله",
            "اللي جاي أحسن", "أنا مش شايل هم", "إنت مش شايفني",
            "بقول الحمد لله علشان خاطري", "مش عايز أتعب حد معايا",
            "أنا تعبان بس مش مهم", "الهم ما يخففش", "أنا خلاص تعودت",
        ],
        "context_boosts": {
            "problem_keywords": ["فلوس", "مال", "شغل", "تعب", "مرض", "وجع", "ضغط", "هم"],
            "preceded_by_negative": True,
        },
        "weight": 0.85,
    },
    "anxiety_disguised": {
        "patterns": [
            "ربنا يستر", "إن شاء الله تعدي", "الواحد بيعمل اللي عليه",
            "بكرة يوم جديد", "الله كريم", "إن شاء الله خير",
            "ربنا يكتب اللي فيه الخير", "مش عارف إيه اللي جاي",
            "أنا مش مرتاح", "في حاجة جوايا مش مطمناني",
            "الواحد خايف من بكرة", "مش قادر أنام الليالي دي", "ربنا يسهل",
        ],
        "context_boosts": {
            "problem_keywords": ["بكرة", "المستقبل", "شغل", "فلوس", "أولاد", "مسؤولية"],
            "preceded_by_uncertainty": True,
        },
        "weight": 0.80,
    },
    "anger_disguised": {
        "patterns": [
            "حسبي الله ونعم الوكيل", "اللي فيه الخير يقدمه الله",
            "أنا مش عايز أتكلم", "خلاص بقى", "ربنا ياخدهم",
            "أنا زهقت", "مش قادر أستحمل", "كفاية كده",
            "أنا هادي بس جوايا نار", "العدل ربنا هو اللي بيجيبه",
            "أنا مش هرد", "سيبتها على الله",
        ],
        "context_boosts": {
            "problem_keywords": ["ظلم", "حق", "غش", "كذب", "خيانة", "نصب"],
            "preceded_by_conflict": True,
        },
        "weight": 0.90,
    },
}

# بناء القاموس العكسي للبحث السريع
REVERSE_EMOTION_MAP = {}
for emotion_type, data in ARABIC_CONTEXTUAL_PATTERNS.items():
    for pattern in data["patterns"]:
        REVERSE_EMOTION_MAP[pattern] = {
            "emotion_type": emotion_type,
            "weight": data["weight"],
        }

logger.info("✅ Arabic patterns dictionary loaded (Part 1/3)")

# ============================================================
# تكملة القاموس (3 فئات إضافية)
# ============================================================

ARABIC_CONTEXTUAL_PATTERNS.update({
    "joy_disguised": {
        "patterns": [
            "الحمد لله", "ربنا أكرمنا", "ده من فضل ربي",
            "ربنا رزقني من حيث لا أحتسب", "دي نعمة من ربنا",
            "ما شاء الله", "ربنا يحفظها", "اللهم لا حسد",
            "أنا مش مصدق", "حاجة تفرح بجد", "ربنا عوضني خير",
        ],
        "context_boosts": {
            "problem_keywords": ["نجاح", "فلوس", "شغل جديد", "زواج", "بيت", "ترقية"],
            "preceded_by_positive": True,
        },
        "weight": 0.75,
    },
    "shame_disguised": {
        "patterns": [
            "أنا مش قد كده", "دي ستر وغطا من ربنا",
            "أنا أصلاً مش فاهم حاجة", "الناس دي أكبر مني",
            "أنا خايف أتكلم قدامهم", "مش عايز حد ياخد عني فكرة وحشة",
            "أنا اللي غلطان أكيد", "مش عايز أحرج حد",
        ],
        "context_boosts": {
            "problem_keywords": ["ناس", "قدام", "كلام", "حد", "قالوا", "سمعة"],
        },
        "weight": 0.70,
    },
    "despair_disguised": {
        "patterns": [
            "أنا تعبت من كل حاجة", "مش فارقة معايا خلاص",
            "الواحد بيعمل إيه تاني", "أنا وصلت لطريق مسدود",
            "مش قادر أقوم من السرير", "أنا مش عايز حاجة تاني",
            "خلاص أنا استسلمت", "الواحد يئس من الفرج",
        ],
        "context_boosts": {
            "problem_keywords": ["تعب", "زهق", "ملل", "نوم", "فراغ", "وحدة"],
            "preceded_by_repeated_failure": True,
        },
        "weight": 0.95,
    },
})

# تحديث القاموس العكسي
REVERSE_EMOTION_MAP.clear()
for emotion_type, data in ARABIC_CONTEXTUAL_PATTERNS.items():
    for pattern in data["patterns"]:
        REVERSE_EMOTION_MAP[pattern] = {
            "emotion_type": emotion_type,
            "weight": data["weight"],
        }

# ============================================================
# دوال الكشف المباشر واستخراج المحفزات
# ============================================================

def detect_direct_emotion_arabic(text: str) -> Optional[str]:
    """كشف العواطف المباشرة بالعربية."""
    direct_map = {
        "sadness": ["حزين", "زعلان", "مكتئب", "مهموم", "مقهور", "مجروح"],
        "fear": ["خايف", "قلقان", "مرعوب", "متوتر", "مذعور"],
        "anger": ["غضبان", "عصبي", "متضايق", "قرفان", "مستفز"],
        "joy": ["فرحان", "مبسوط", "سعيد", "مستانس", "مبتهج"],
        "shame": ["خجلان", "محرج", "متكسف"],
    }
    for emotion, words in direct_map.items():
        for word in words:
            if word in text:
                return emotion
    return None


def extract_trigger(text: str) -> Optional[str]:
    """استخراج المحفز العاطفي من النص العربي."""
    trigger_keywords = {
        "مال": "money", "فلوس": "money", "شغل": "work", "عمل": "work",
        "أهل": "family", "عائلة": "family", "صحة": "health", "مرض": "health",
        "حب": "love", "زواج": "marriage", "أصدقاء": "friends",
        "وحدة": "loneliness", "مستقبل": "future",
    }
    for word, category in trigger_keywords.items():
        if word in text:
            return category
    return None

logger.info("✅ Arabic patterns dictionary + helper functions loaded (Part 2/3)")

# ============================================================
# المحرك السياقي: يفهم التعبير من السياق المحيط
# ============================================================

def analyze_arabic_context(
    text: str,
    previous_messages: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    تحليل سياقي عميق. يفحص النص + آخر 5 رسائل.
    يرفع أو يخفض الثقة حسب السياق المحيط.
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()
    detected_emotions = []
    
    # 1. فحص الأنماط العربية المعروفة
    for pattern, info in REVERSE_EMOTION_MAP.items():
        if pattern in text_lower:
            real_emotion = info["emotion_type"]
            confidence = info["weight"]
            context_multiplier = 1.0
            context_reason = ""
            
            pattern_data = ARABIC_CONTEXTUAL_PATTERNS.get(real_emotion, {})
            
            # 2. تحليل السياق السابق
            if previous_messages and pattern_data.get("context_boosts"):
                boosts = pattern_data["context_boosts"]
                
                if "problem_keywords" in boosts:
                    for prev_msg in previous_messages[-3:]:
                        for kw in boosts["problem_keywords"]:
                            if kw in prev_msg.lower():
                                context_multiplier += 0.15
                                context_reason = f"سياق سابق: '{kw}'"
                
                if boosts.get("preceded_by_negative"):
                    all_neg = all(
                        any(w in m.lower() for w in ["تعب", "هم", "مشكلة", "سيء", "صعب", "وجع"])
                        for m in previous_messages[-2:]
                    )
                    if all_neg and previous_messages:
                        context_multiplier += 0.25
                        context_reason += " | سياق سلبي متكرر"
                
                if boosts.get("preceded_by_positive"):
                    all_pos = all(
                        any(w in m.lower() for w in ["حمد", "نجاح", "خير", "فرح", "مبسوط"])
                        for m in previous_messages[-2:]
                    )
                    if all_pos and previous_messages:
                        context_multiplier += 0.20
                        context_reason += " | سياق إيجابي سابق"
            
            final_confidence = min(confidence * context_multiplier, 1.0)
            
            base_emotion_map = {
                "sadness_disguised": "sadness", "anxiety_disguised": "fear",
                "anger_disguised": "anger", "joy_disguised": "joy",
                "shame_disguised": "shame", "despair_disguised": "sadness",
            }
            
            detected_emotions.append({
                "surface_expression": text_clean[:200],
                "real_emotion": base_emotion_map.get(real_emotion, "neutral"),
                "arabic_category": real_emotion,
                "confidence": round(final_confidence, 2),
                "context_reason": context_reason or "تطابق مباشر",
                "expressed_as": pattern,
            })
    
    # 3. إذا لم يُكتشف شيء، افحص العواطف المباشرة
    if not detected_emotions:
        direct = detect_direct_emotion_arabic(text_lower)
        if direct:
            detected_emotions.append({
                "surface_expression": text_clean[:200],
                "real_emotion": direct,
                "arabic_category": f"direct_{direct}",
                "confidence": 0.70,
                "context_reason": "تعبير مباشر",
                "expressed_as": text_clean[:100],
            })
    
    if not detected_emotions:
        return {
            "real_emotion": "neutral", "confidence": 0.5,
            "detected_patterns": [], "cultural_analysis": "لا نمط مكتشف",
        }
    
    detected_emotions.sort(key=lambda x: x["confidence"], reverse=True)
    best = detected_emotions[0]
    
    return {
        "real_emotion": best["real_emotion"],
        "confidence": best["confidence"],
        "detected_patterns": detected_emotions[:3],
        "cultural_analysis": (
            f"حقيقية: {best['real_emotion']} | "
            f"تصنيف: {best['arabic_category']} | "
            f"سبب: {best['context_reason']}"
        ),
    }


# ============================================================
# تخزين الذاكرة العاطفية مع ربط تلقائي
# ============================================================

async def store_emotional_memory(
    user_id: str,
    expressed_text: str,
    detected_emotion: Dict[str, Any],
    trigger: Optional[str] = None,
    cultural_context: Optional[str] = None,
    previous_messages: Optional[List[str]] = None,
    mentioned_persons: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    تخزين ذاكرة عاطفية كاملة مع ربط تلقائي بالأشخاص.
    تعيد إشارات للطبقات الأخرى (Graph, PersonNode).
    """
    db = get_db()
    
    arabic_analysis = analyze_arabic_context(expressed_text, previous_messages)
    expressed_emotion = detected_emotion.get("primary", "neutral")
    real_emotion = arabic_analysis["real_emotion"]
    
    if arabic_analysis["confidence"] > 0.7:
        real_emotion = arabic_analysis["real_emotion"]
    
    intensity = detected_emotion.get("intensity", 0.5)
    if arabic_analysis["confidence"] > 0.85:
        intensity = min(intensity + 0.2, 1.0)
    
    person_links = []
    if mentioned_persons:
        for p in mentioned_persons:
            person_links.append({
                "person_id": p.get("id"),
                "person_name": p.get("name"),
                "relationship_type": p.get("relationship_type", "unknown"),
                "emotion_toward_person": real_emotion,
            })
    
    try:
        payload = {
            "user_id": user_id,
            "expressed_text": expressed_text[:500],
            "expressed_emotion": expressed_emotion,
            "real_emotion": real_emotion,
            "intensity": round(intensity, 2),
            "confidence": arabic_analysis["confidence"],
            "trigger": trigger or extract_trigger(expressed_text),
            "cultural_context": cultural_context or arabic_analysis.get("cultural_analysis", ""),
            "valence": detected_emotion.get("valence", 0.0),
            "person_links": person_links,
            "arabic_category": arabic_analysis.get("detected_patterns", [{}])[0].get("arabic_category", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = db.table(TABLE_NAME).insert(payload).execute()
        memory_id = result.data[0]["id"] if result.data else ""
        
        logger.info(f"🧠 عاطفة: {expressed_emotion} → {real_emotion} | "
                   f"ثقة: {arabic_analysis['confidence']:.0%} | أشخاص: {len(person_links)}")
        
        return {
            "id": memory_id,
            "real_emotion": real_emotion,
            "confidence": arabic_analysis["confidence"],
            "person_links": person_links,
            "trigger": trigger or extract_trigger(expressed_text),
            "needs_graph_update": len(person_links) > 0,
        }
    except Exception as e:
        logger.error(f"فشل تخزين الذاكرة العاطفية: {e}")
        return {"id": "", "real_emotion": "neutral", "confidence": 0, "person_links": [], "needs_graph_update": False}


# ============================================================
# تحليل الأنماط العاطفية العميقة عبر الزمن
# ============================================================

async def get_emotional_patterns(
    user_id: str,
    days: int = 30,
) -> Dict[str, Any]:
    """
    تحليل أنماط: توزيع، تحولات، أيام أسبوع، توصيات.
    """
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        result = (
            db.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .execute()
        )
        
        if not result.data or len(result.data) < 3:
            return {
                "dominant_emotion": "neutral",
                "emotion_distribution": {},
                "patterns": ["بيانات غير كافية"],
                "recommendation": "يحتاج التوأم مزيداً من التفاعل",
            }
        
        memories = result.data
        emotion_counts = Counter(m.get("real_emotion", "neutral") for m in memories)
        total = len(memories)
        distribution = {k: round(v/total, 2) for k, v in emotion_counts.most_common()}
        dominant = emotion_counts.most_common(1)[0][0]
        
        patterns = []
        
        if distribution.get(dominant, 0) > 0.5:
            patterns.append(f"هيمنة '{dominant}' بنسبة {distribution[dominant]:.0%}")
        
        emotions_ordered = [m.get("real_emotion") for m in memories[:20]]
        transitions = sum(1 for i in range(1, len(emotions_ordered)) if emotions_ordered[i] != emotions_ordered[i-1])
        if transitions > len(emotions_ordered) * 0.5:
            patterns.append("تقلبات عاطفية حادة")
        
        recent_5 = [m.get("real_emotion") for m in memories[:5]]
        older_5 = [m.get("real_emotion") for m in memories[-5:]]
        recent_neg = sum(1 for e in recent_5 if e in ["sadness", "fear", "anger"])
        older_neg = sum(1 for e in older_5 if e in ["sadness", "fear", "anger"])
        if recent_neg < older_neg:
            patterns.append("تحسن عاطفي مؤخراً")
        elif recent_neg > older_neg:
            patterns.append("تدهور عاطفي يستحق الانتباه")
        
        weekday_emotions = {}
        for m in memories:
            created = m.get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    day = dt.strftime("%A")
                    weekday_emotions.setdefault(day, []).append(m.get("real_emotion"))
                except:
                    pass
        for day, emos in weekday_emotions.items():
            neg_count = sum(1 for e in emos if e in ["sadness", "fear", "anger"])
            if len(emos) >= 3 and neg_count / len(emos) > 0.7:
                patterns.append(f"أيام {day} تميل للسلبية")
        
        recommendation = generate_emotional_recommendation(dominant, distribution, patterns)
        
        return {
            "dominant_emotion": dominant,
            "emotion_distribution": distribution,
            "total_memories_analyzed": total,
            "transitions_detected": transitions,
            "patterns": patterns,
            "recommendation": recommendation,
        }
    except Exception as e:
        logger.error(f"فشل تحليل الأنماط: {e}")
        return {"dominant_emotion": "neutral", "patterns": ["خطأ في التحليل"]}


def generate_emotional_recommendation(
    dominant: str,
    distribution: Dict[str, float],
    patterns: List[str],
) -> str:
    """توليد توصية للتوأم بناءً على الأنماط."""
    if dominant == "sadness" and distribution.get("sadness", 0) > 0.4:
        return "المستخدم يحتاج رفعة معنوية. كن دافئاً ومتفائلاً."
    elif dominant == "fear" and distribution.get("fear", 0) > 0.4:
        return "المستخدم قلق. طمئنه دون وعود زائفة."
    elif dominant == "anger" and distribution.get("anger", 0) > 0.3:
        return "المستخدم غاضب. استمع أولاً ولا تنصح مباشرة."
    elif dominant == "joy" and distribution.get("joy", 0) > 0.5:
        return "المستخدم إيجابي. شجعه على البناء على هذا الزخم."
    return "كن متوازناً. لاحظ التحولات العاطفية واستجب لها."


# ============================================================
# دالة المنسق الشاملة
# ============================================================

async def get_emotional_state_for_response(
    user_id: str,
    current_message: str,
    previous_messages: Optional[List[str]] = None,
    mentioned_persons: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    الدالة الرئيسية التي يستدعيها المنسق قبل توليد الرد.
    تجمع التحليل اللحظي + التاريخي + توصية.
    """
    current_analysis = analyze_arabic_context(current_message, previous_messages)
    historical_patterns = await get_emotional_patterns(user_id, days=14)
    
    return {
        "current_emotion": current_analysis["real_emotion"],
        "current_confidence": current_analysis["confidence"],
        "cultural_note": current_analysis.get("cultural_analysis", ""),
        "dominant_historical": historical_patterns.get("dominant_emotion", "neutral"),
        "historical_patterns": historical_patterns.get("patterns", []),
        "recommendation": historical_patterns.get("recommendation", ""),
        "is_culturally_disguised": current_analysis["confidence"] > 0.7,
        "mentioned_persons_count": len(mentioned_persons) if mentioned_persons else 0,
    }


logger.info("✅ Emotional Memory Engine fully initialized")
