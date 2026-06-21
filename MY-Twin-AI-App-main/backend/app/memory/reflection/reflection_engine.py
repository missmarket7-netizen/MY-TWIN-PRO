"""
Reflection Engine - Layer 8 of TCMA
====================================
يراقب التفاعلات ويستنتج حقائق جديدة عن المستخدم.
لا يخزن ما يقال فقط، بل يفهم ما يُعنى.
يدعم العقلية العربية (الصراعات الخفية) والغربية.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from collections import Counter
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("reflection_engine")
TABLE_NAME = "reflection_insights"

# ============================================================
# الجزء 1: أنماط الاستنتاج
# ============================================================

REFLECTION_PATTERNS = {
    # --- صراعات الهوية العربية ---
    "identity_conflict": {
        "triggers_ar": [
            ("أريد", "لكن", "أهلي"),
            ("نفسي", "بس", "العائلة"),
            ("حلمي", "لكن", "الظروف"),
            ("أحب", "لكن", "مجتمعنا"),
            ("طموحي", "بس", "خايف"),
        ],
        "triggers_en": [
            ("want to", "but", "family"),
            ("dream", "but", "reality"),
            ("love", "but", "society"),
            ("ambition", "but", "fear"),
        ],
        "insight_template_ar": "يعيش صراعاً بين {desire} و{obstacle}",
        "insight_template_en": "Experiencing conflict between {desire} and {obstacle}",
    },
    
    # --- أنماط التجنب العاطفي ---
    "emotional_avoidance": {
        "triggers_ar": [
            "مش عايز أتكلم في الموضوع",
            "خلينا في حاجة تانية",
            "مش مهم",
            "فاكس",
        ],
        "triggers_en": [
            "don't want to talk about it",
            "let's change the subject",
            "it's nothing",
            "whatever",
        ],
        "insight_template_ar": "يتجنب الحديث عن {topic}",
        "insight_template_en": "Avoids discussing {topic}",
    },
    
    # --- قيم متكررة ---
    "core_value": {
        "triggers_ar": [
            "المهم عندي", "أهم حاجة", "اللي يهمني",
            "أنا أؤمن بـ", "مبدأي", "قناعتي",
        ],
        "triggers_en": [
            "what matters to me", "most important", "I believe in",
            "my principle", "my conviction",
        ],
        "insight_template_ar": "يؤمن بقيمة: {value}",
        "insight_template_en": "Core value: {value}",
    },
    
    # --- مخاوف متكررة ---
    "recurring_fear": {
        "triggers_ar": [
            "خايف من", "قلقان على", "مش مطمن على",
            "بفكر كتير في", "اللي مقلقني",
        ],
        "triggers_en": [
            "afraid of", "worried about", "anxious about",
            "keeps me up at night", "what scares me",
        ],
        "insight_template_ar": "لديه خوف متكرر من {fear}",
        "insight_template_en": "Recurring fear of {fear}",
    },
    
    # --- طموحات مخفية ---
    "hidden_ambition": {
        "triggers_ar": [
            "نفسي أعمل", "لو كان بإيدي", "حلمي إني",
            "في يوم من الأيام", "أنا بطمح لـ",
        ],
        "triggers_en": [
            "I wish I could", "someday I want to", "my dream is",
            "if I had the chance", "I aspire to",
        ],
        "insight_template_ar": "يطمح سراً لـ: {ambition}",
        "insight_template_en": "Secretly aspires to: {ambition}",
    },
}

# ============================================================
# الجزء 2: محرك الاستنتاج
# ============================================================

def extract_reflections(text: str, lang: str = "ar") -> List[Dict[str, Any]]:
    """
    يستخرج الاستنتاجات من النص بناءً على الأنماط.
    """
    reflections = []
    text_lower = text.lower()

    for pattern_type, pattern_data in REFLECTION_PATTERNS.items():
        triggers = pattern_data.get(f"triggers_{lang}", []) + pattern_data.get("triggers_en", [])
        
        for trigger_set in triggers:
            if isinstance(trigger_set, tuple):
                # نمط متعدد الكلمات
                if all(word.lower() in text_lower for word in trigger_set):
                    # استخراج الكلمات بين المحفزات
                    parts = {}
                    for i, word in enumerate(trigger_set):
                        key = ["desire", "obstacle", "topic", "value", "fear", "ambition"][i] if i < 6 else f"part_{i}"
                        idx = text_lower.find(word.lower())
                        if idx >= 0:
                            after = text_lower[idx + len(word):].strip()[:50]
                            parts[key] = after.split(".")[0].strip()
                    
                    template_key = f"insight_template_{lang}"
                    template = pattern_data.get(template_key, pattern_data.get("insight_template_en", ""))
                    
                    insight_text = template.format(**parts) if parts else template
                    
                    reflections.append({
                        "type": pattern_type,
                        "insight": insight_text,
                        "confidence": 0.7,
                        "source_text": text[:200],
                    })
            else:
                # نمط كلمة واحدة
                if trigger_set in text_lower:
                    template_key = f"insight_template_{lang}"
                    template = pattern_data.get(template_key, pattern_data.get("insight_template_en", ""))
                    
                    reflections.append({
                        "type": pattern_type,
                        "insight": template.format(**{"topic": text[:50]}),
                        "confidence": 0.5,
                        "source_text": text[:200],
                    })

    return reflections


# ============================================================
# الجزء 3: تخزين وتراكم الاستنتاجات
# ============================================================

async def store_reflection(
    user_id: str,
    insight_type: str,
    insight_text: str,
    confidence: float = 0.5,
    source_message_id: Optional[str] = None,
    related_person_id: Optional[str] = None,
    related_emotion: Optional[str] = None,
    language: str = "ar",
) -> str:
    """
    يخزن استنتاجاً جديداً. إذا كان موجوداً مسبقاً، يرفع ثقته.
    """
    db = get_db()
    
    try:
        # فحص إذا كان الاستنتاج موجوداً مسبقاً
        existing = (
            db.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .eq("insight_type", insight_type)
            .eq("insight_text", insight_text)
            .execute()
        )
        
        if existing.data and len(existing.data) > 0:
            # تحديث: رفع الثقة
            old = existing.data[0]
            new_confidence = min(old.get("confidence", 0.5) + 0.1, 1.0)
            db.table(TABLE_NAME).update({
                "confidence": new_confidence,
                "occurrence_count": old.get("occurrence_count", 1) + 1,
                "last_observed": datetime.now(timezone.utc).isoformat(),
            }).eq("id", old["id"]).execute()
            
            logger.info(f"🔄 استنتاج معزز: {insight_text} | ثقة: {new_confidence:.0%}")
            return old["id"]
        
        # إنشاء استنتاج جديد
        payload = {
            "user_id": user_id,
            "insight_type": insight_type,
            "insight_text": insight_text,
            "confidence": confidence,
            "source_message_id": source_message_id,
            "related_person_id": related_person_id,
            "related_emotion": related_emotion,
            "language": language,
            "occurrence_count": 1,
            "first_observed": datetime.now(timezone.utc).isoformat(),
            "last_observed": datetime.now(timezone.utc).isoformat(),
        }
        result = db.table(TABLE_NAME).insert(payload).execute()
        
        if result.data:
            logger.info(f"💡 استنتاج جديد: {insight_text}")
            return result.data[0]["id"]
        
    except Exception as e:
        logger.error(f"فشل تخزين الاستنتاج: {e}")
    
    return ""


# ============================================================
# الجزء 4: تحليل دوري للاستنتاجات المتراكمة
# ============================================================

async def get_user_insights(
    user_id: str,
    min_confidence: float = 0.6,
) -> Dict[str, Any]:
    """
    يسترجع كل الاستنتاجات عن المستخدم، مرتبة حسب الثقة.
    """
    db = get_db()
    try:
        result = (
            db.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .gte("confidence", min_confidence)
            .order("confidence", desc=True)
            .limit(30)
            .execute()
        )
        
        if not result.data:
            return {
                "insights": [],
                "summary": "لا توجد استنتاجات كافية بعد",
            }
        
        insights = result.data
        
        # تصنيف الاستنتاجات
        by_type = {}
        for ins in insights:
            t = ins.get("insight_type", "other")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(ins["insight_text"])
        
        # تلخيص
        summary_parts = []
        for t, texts in by_type.items():
            type_names = {
                "identity_conflict": "صراعات الهوية",
                "emotional_avoidance": "تجنب عاطفي",
                "core_value": "قيم أساسية",
                "recurring_fear": "مخاوف متكررة",
                "hidden_ambition": "طموحات مخفية",
            }
            type_name = type_names.get(t, t)
            summary_parts.append(f"{type_name}: {len(texts)} استنتاجات")
        
        return {
            "insights": [{
                "type": ins["insight_type"],
                "text": ins["insight_text"],
                "confidence": ins["confidence"],
                "occurrences": ins.get("occurrence_count", 1),
            } for ins in insights],
            "summary": " | ".join(summary_parts),
            "total_insights": len(insights),
        }
        
    except Exception as e:
        logger.error(f"فشل استرجاع الاستنتاجات: {e}")
        return {"insights": [], "summary": "خطأ في الاسترجاع"}


# ============================================================
# الجزء 5: دالة المنسق الشاملة
# ============================================================

async def process_message_for_reflections(
    user_id: str,
    message: str,
    language: str = "ar",
    detected_emotion: Optional[str] = None,
    mentioned_person_id: Optional[str] = None,
    message_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    تعالج الرسالة وتستخرج الاستنتاجات وتخزنها.
    تستدعى من المنسق بعد كل رسالة.
    """
    # 1. استخراج الاستنتاجات
    reflections = extract_reflections(message, language)
    
    if not reflections:
        return []
    
    stored = []
    for ref in reflections:
        ref_id = await store_reflection(
            user_id=user_id,
            insight_type=ref["type"],
            insight_text=ref["insight"],
            confidence=ref["confidence"],
            source_message_id=message_id,
            related_person_id=mentioned_person_id,
            related_emotion=detected_emotion,
            language=language,
        )
        if ref_id:
            stored.append({**ref, "id": ref_id})
    
    return stored


logger.info("✅ Reflection Engine initialized")
