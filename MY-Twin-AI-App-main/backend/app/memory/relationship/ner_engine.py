"""
NER Engine – Named Entity Recognition for Arabic & Western
===========================================================
يكتشف أسماء العلم المنعزلة (بدون ألقاب).
يفهم "محمد قال لي" مثلما يفهم "أخي محمد".
يدعم العربية والإنجليزية.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Set

logger = logging.getLogger("ner_engine")

# ============================================================
# قوائم أسماء العلم الشائعة (عربي وغربي)
# ============================================================
ARABIC_COMMON_NAMES = {
    # ذكور
    "محمد", "أحمد", "علي", "عمر", "حسن", "حسين", "محمود", "إبراهيم",
    "خالد", "عبدالله", "يوسف", "طارق", "سامي", "ناصر", "فيصل", "سلمان",
    "ماجد", "وليد", "رامي", "باسل", "كريم", "أمين", "هشام", "عادل",
    "سعيد", "جابر", "مروان", "زياد", "عماد", "أيمن", "بشار", "غسان",
    # إناث
    "فاطمة", "مريم", "نورة", "سارة", "عائشة", "زينب", "رقية", "خديجة",
    "ليلى", "هدى", "منى", "دلال", "نوال", "سمية", "أمل", "حنان",
    "جميلة", "سعاد", "نادرة", "رنا", "لينا", "دانة", "غادة", "لمى",
}

WESTERN_COMMON_NAMES = {
    # Male
    "john", "james", "robert", "michael", "david", "william", "richard",
    "joseph", "thomas", "charles", "christopher", "daniel", "matthew",
    "anthony", "mark", "donald", "steven", "paul", "andrew", "joshua",
    "kenneth", "kevin", "brian", "george", "edward", "ronald", "timothy",
    # Female
    "mary", "patricia", "jennifer", "linda", "barbara", "elizabeth",
    "susan", "jessica", "sarah", "karen", "nancy", "lisa", "betty",
    "margaret", "sandra", "ashley", "kimberly", "emily", "donna",
    "michelle", "dorothy", "carol", "amanda", "melissa", "deborah",
}

# أسماء يمكن أن تكون علاقة أو اسم علم (تحتاج سياق)
AMBIGUOUS_NAMES = {
    "علي": "قد يكون اسماً أو حرف جر",
    "أحمد": "قد يكون اسماً أو فعل 'أحمد الله'",
    "حسن": "قد يكون اسماً أو صفة",
    "سالم": "قد يكون اسماً أو صفة",
    "rose": "may be name or flower",
    "bill": "may be name or invoice",
}

# ============================================================
# كاشف الأسماء من السياق
# ============================================================
def detect_names_from_text(text: str, lang: str = "ar") -> List[Dict[str, Any]]:
    """
    يكتشف أسماء العلم في النص بدون الاعتماد على ألقاب.
    """
    found_names = []
    text_lower = text.lower()

    # 1. اختيار القاموس المناسب
    names_set = ARABIC_COMMON_NAMES if lang == "ar" else WESTERN_COMMON_NAMES
    # دمج القاموسين للدقة
    all_names = ARABIC_COMMON_NAMES | WESTERN_COMMON_NAMES

    # 2. البحث عن كل اسم في النص
    for name in all_names:
        name_lower = name.lower()
        # بحث ككلمة كاملة (وليس جزءاً من كلمة)
        pattern = re.compile(r'\b' + re.escape(name_lower) + r'\b', re.IGNORECASE)
        match = pattern.search(text_lower)
        
        if match:
            # استخراج السياق المحيط (الكلمات قبل وبعد)
            idx = match.start()
            before = text_lower[max(0, idx-30):idx].strip()
            after = text_lower[idx+len(name):idx+len(name)+50].strip()

            # فحص إذا كان مسبوقاً بلقب (سبق اكتشافه في PersonNode)
            preceded_by_title = bool(re.search(
                r'(أخي|أختي|عمي|خالي|صديقي|زميلي|my|brother|sister|friend)\s*$',
                before
            ))

            # إذا كان مسبوقاً بلقب، تجاهله (PersonNode سيكتشفه)
            if preceded_by_title:
                continue

            # فحص الكلمات المحيطة للتأكد أنه اسم علم وليس صفة
            confidence = 0.6  # ثقة ابتدائية

            # السياق العربي
            if lang == "ar":
                # أفعال وكلمات تدل أن الاسم فاعل
                person_indicators = [
                    r'\b(قال|يقول|تكلم|يتكلم|ذهب|يذهب|جاء|يجيء|فعل|يفعل)\b',
                    r'\b(لي|عندي|مع|من|إلى|على|عن)\s*$',
                    r'\bيا\s*$',
                ]
                for indicator in person_indicators:
                    if re.search(indicator, before):
                        confidence += 0.2
                        break
                # إذا كان الاسم بعده فعل
                if re.search(r'^\s*(قال|يقول|فعل|ذهب|جاء)', after):
                    confidence += 0.15

            # السياق الإنجليزي
            else:
                person_indicators = [
                    r'\b(said|told|went|came|did|made|is|was)\b',
                    r'\b(to|from|with|for|by)\s*$',
                ]
                for indicator in person_indicators:
                    if re.search(indicator, before):
                        confidence += 0.2
                        break
                if re.search(r'^\s*(said|went|is|was|did)', after):
                    confidence += 0.15

            # إذا كان من الأسماء الغامضة، اخفض الثقة
            if name_lower in AMBIGUOUS_NAMES:
                confidence -= 0.15

            # اسم يبدأ بحرف كبير في الإنجليزية يزيد الثقة
            if lang == "en" and name[0].isupper():
                confidence += 0.1

            found_names.append({
                "name": name,
                "confidence": min(confidence, 1.0),
                "context_before": before[-20:],
                "context_after": after[:20],
                "language": lang,
            })

    # 3. إزالة التكرارات (نفس الاسم يظهر مرتين)
    unique = {}
    for n in found_names:
        key = n["name"].lower()
        if key not in unique or n["confidence"] > unique[key]["confidence"]:
            unique[key] = n

    return sorted(unique.values(), key=lambda x: x["confidence"], reverse=True)


# ============================================================
# دالة التعاون (Co-occurrence) – اكتشاف علاقات بين شخصين
# ============================================================
def detect_co_occurrence(
    text: str,
    persons: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    إذا ذُكر شخصان معاً في رسالة واحدة، نسجل ارتباطهما.
    """
    if len(persons) < 2:
        return []

    co_occurrences = []
    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            co_occurrences.append({
                "person_a": persons[i]["name"],
                "person_b": persons[j]["name"],
                "relation_hint": "mentioned_together",
                "context": text[:200],
            })

    return co_occurrences


logger.info("✅ NER Engine initialized")
