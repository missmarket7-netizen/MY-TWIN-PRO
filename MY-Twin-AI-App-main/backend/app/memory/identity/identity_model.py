"""
Identity Model - Layer 9 of TCMA
=================================
نموذج هوية متعدد الأبعاد. يستنتج تلقائياً من المحادثات.
يفهم الصراعات العربية (الفرد vs العائلة) والغربية.
يتكامل مع Reflection Engine و PersonNode.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("identity_model")
TABLE_NAME = "identity_model"
TABLE_EVOLUTION = "identity_evolution"

# ============================================================
# أبعاد الهوية (عربي وغربي)
# ============================================================
IDENTITY_DIMENSIONS = {
    "self_view": "كيف يرى المستخدم نفسه",
    "family_role": "دوره في عائلته",
    "social_role": "دوره في المجتمع/أصدقائه",
    "religious_identity": "هويته الدينية أو الروحية",
    "cultural_conflicts": "صراعاته الثقافية",
    "core_values": "قيمه الأساسية",
    "aspirations": "طموحاته وأحلامه",
    "fears": "مخاوفه العميقة",
}

# ============================================================
# تخزين لقطة جديدة للهوية
# ============================================================
async def build_identity_model(
    user_id: str,
    self_view: Optional[str] = None,
    traits: Optional[List[str]] = None,
    family_role: Optional[str] = None,
    social_role: Optional[str] = None,
    religious_identity: Optional[str] = None,
    cultural_conflicts: Optional[List[str]] = None,
    core_values: Optional[List[str]] = None,
    aspirations: Optional[List[str]] = None,
    fears: Optional[List[str]] = None,
    source_message: Optional[str] = None,
) -> str:
    """تخزين لقطة جديدة لنموذج الهوية."""
    db = get_db()
    try:
        payload = {
            "user_id": user_id,
            "self_view": self_view or "",
            "traits": traits or [],
            "family_role": family_role or "",
            "social_role": social_role or "",
            "religious_identity": religious_identity or "",
            "cultural_conflicts": cultural_conflicts or [],
            "core_values": core_values or [],
            "aspirations": aspirations or [],
            "fears": fears or [],
            "source_message": source_message,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = db.table(TABLE_NAME).insert(payload).execute()
        return result.data[0]["id"] if result.data else ""
    except Exception as e:
        logger.error(f"فشل بناء نموذج الهوية: {e}")
        return ""


# ============================================================
# استرجاع أحدث هوية
# ============================================================
async def get_identity(user_id: str) -> Dict[str, Any]:
    """يسترجع أحدث نموذج هوية."""
    db = get_db()
    try:
        result = (
            db.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .single()
            .execute()
        )
        if result.data:
            return result.data
        return {
            "self_view": "غير معروف",
            "traits": [],
            "family_role": "غير معروف",
            "social_role": "غير معروف",
            "religious_identity": "غير معروف",
            "cultural_conflicts": [],
            "core_values": [],
            "aspirations": [],
            "fears": [],
        }
    except Exception:
        return {"self_view": "غير معروف", "traits": []}


# ============================================================
# تتبع تطور الهوية عبر الزمن
# ============================================================
async def get_identity_evolution(
    user_id: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """يسترجع تاريخ تطور الهوية."""
    db = get_db()
    try:
        result = (
            db.table(TABLE_NAME)
            .select("created_at,self_view,traits,family_role,social_role")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


logger.info("✅ Identity Model Part 1 loaded")

# ============================================================
# محرك تحليل الهوية من الرسائل (تلقائي)
# ============================================================
from app.memory.reflection.reflection_engine import get_user_insights
from app.memory.relationship.person_node import get_person_network

IDENTITY_KEYWORDS = {
    "family_role": {
        "ar": ["أنا الابن", "أنا الأب", "أنا الأخ", "أنا المسؤول عن", "أنا اللي بساعد أهلي"],
        "en": ["I am the son", "I am the father", "I am the brother", "I take care of"],
    },
    "social_role": {
        "ar": ["أنا الصديق", "أنا الزميل", "أنا المدير", "أنا القائد", "أنا الشخص اللي"],
        "en": ["I am the friend", "I am the colleague", "I am the manager", "I am the leader"],
    },
    "self_view": {
        "ar": ["أنا شخص", "أنا إنسان", "أنا اللي", "شخصيتي", "طبعي"],
        "en": ["I am a", "I'm a", "my personality", "I tend to"],
    },
    "religious_identity": {
        "ar": ["أنا ملتزم", "أنا متدين", "أنا بصلي", "أنا مؤمن", "ربنا", "ديني"],
        "en": ["I am religious", "I believe in God", "I pray", "my faith"],
    },
}


def extract_identity_signals(
    text: str,
    language: str = "ar",
) -> Dict[str, List[str]]:
    """يستخرج إشارات الهوية من النص."""
    signals = {}
    text_lower = text.lower()

    for dimension, lang_dict in IDENTITY_KEYWORDS.items():
        keywords = lang_dict.get(language, []) + lang_dict.get("en", [])
        found = []
        for kw in keywords:
            if kw.lower() in text_lower:
                # استخراج الجزء المهم بعد الكلمة المفتاحية
                idx = text_lower.find(kw.lower())
                snippet = text[idx:idx+100].strip()
                found.append(snippet)
        if found:
            signals[dimension] = found

    return signals


async def analyze_and_update_identity(
    user_id: str,
    message: str,
    language: str = "ar",
) -> Dict[str, Any]:
    """
    الدالة الذكية: تستمع للمستخدم، تحلل كلامه، وتحدث هويته تلقائياً.
    تستخدم Reflection Engine و PersonNode.
    """
    # 1. استخراج الإشارات المباشرة من النص
    signals = extract_identity_signals(message, language)

    # 2. جلب الاستنتاجات المتراكمة من Reflection Engine
    insights = await get_user_insights(user_id, min_confidence=0.5)

    # 3. جلب شبكة العلاقات لفهم الدور العائلي
    network = await get_person_network(user_id, min_importance=30)

    # 4. تحليل الدور العائلي
    family_role = None
    family_members = [p for p in network if p.get("relationship_type") == "family"]
    if family_members:
        # من هو الأكثر ذكراً؟
        top_family = sorted(family_members, key=lambda x: x.get("importance_score", 0), reverse=True)[:3]
        family_names = [p["name"] for p in top_family]
        # استنتاج مبسط للدور
        if any("أمي" in n or "ماما" in n or "mom" in n.lower() for n in family_names):
            family_role = f"قريب جداً من والدته: {family_names[0]}"
        elif any("أبوي" in n or "بابا" in n or "dad" in n.lower() for n in family_names):
            family_role = f"قريب جداً من والده: {family_names[0]}"
        else:
            family_role = f"مرتبط عاطفياً بـ: {', '.join(family_names)}"

    # 5. تجميع الصراعات الثقافية من الاستنتاجات
    conflicts = []
    for ins in insights.get("insights", []):
        if ins.get("type") == "identity_conflict":
            conflicts.append(ins["text"])

    # 6. تجميع القيم والمخاوف والطموحات
    values = []
    fears = []
    aspirations = []
    for ins in insights.get("insights", []):
        if ins.get("type") == "core_value":
            values.append(ins["text"])
        elif ins.get("type") == "recurring_fear":
            fears.append(ins["text"])
        elif ins.get("type") == "hidden_ambition":
            aspirations.append(ins["text"])

    # 7. استخراج السمات من self_view
    traits = []
    self_view_text = ""
    if "self_view" in signals:
        self_view_text = signals["self_view"][0]
        # استخراج كلمات أساسية
        trait_words = ["طموح", "صبور", "عصبي", "هادئ", "اجتماعي", "انطوائي",
                      "ambitious", "patient", "calm", "social", "introvert"]
        for word in trait_words:
            if word in self_view_text.lower():
                traits.append(word)

    # 8. تحديث نموذج الهوية
    identity_id = await build_identity_model(
        user_id=user_id,
        self_view=self_view_text or None,
        traits=traits if traits else None,
        family_role=family_role,
        social_role=signals.get("social_role", [None])[0],
        religious_identity=signals.get("religious_identity", [None])[0],
        cultural_conflicts=conflicts if conflicts else None,
        core_values=values if values else None,
        aspirations=aspirations if aspirations else None,
        fears=fears if fears else None,
        source_message=message[:200],
    )

    logger.info(f"🆔 هوية محدثة: {len(conflicts)} صراعات | {len(values)} قيم | {len(traits)} سمات")

    return {
        "identity_id": identity_id,
        "self_view": self_view_text,
        "family_role": family_role,
        "traits": traits,
        "conflicts_detected": len(conflicts),
        "values_detected": len(values),
    }


# ============================================================
# دالة المنسق الشاملة
# ============================================================
async def get_identity_context_for_response(
    user_id: str,
    current_message: str,
    language: str = "ar",
) -> Dict[str, Any]:
    """
    الدالة الرئيسية للمنسق. تعيد فهم التوأم لهوية المستخدم.
    """
    # 1. تحليل وتحديث الهوية
    analysis = await analyze_and_update_identity(user_id, current_message, language)

    # 2. جلب الهوية الحالية
    identity = await get_identity(user_id)

    # 3. جلب تطور الهوية
    evolution = await get_identity_evolution(user_id, limit=5)

    # 4. بناء ملخص للمنسق
    summary = (
        f"المستخدم: {identity.get('self_view', 'غير معروف')} | "
        f"دور عائلي: {identity.get('family_role', 'غير معروف')} | "
        f"قيم: {', '.join(identity.get('core_values', []))} | "
        f"طموحات: {', '.join(identity.get('aspirations', []))}"
    )

    return {
        "identity": identity,
        "summary": summary,
        "evolution_dates": [e.get("created_at") for e in evolution],
        "recent_analysis": analysis,
    }


logger.info("✅ Identity Model Engine initialized (full)")
