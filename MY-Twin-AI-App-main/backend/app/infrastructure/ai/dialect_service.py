"""
Dialect Service – Dialect detection and style guidance.
Migrated from dialect_engine.py with full logic preserved.
"""
import os, logging, re, json, asyncio
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ─ـ أنماط الكشف عن اللهجات ──────────────────────
DIALECT_PATTERNS = {
    "egyptian": [
        r'\b(ازيك|عامل ايه|معلش|كده|بص|يا عم|والله|حاجة|دلوقتي|فلوس|بتاع|عايز|مش|بقى|ليه|إنت|إنتي)\b',
        r'\b(هعمل|هروح|هجيب|هشوف|هقول)\b',
        r'[ةه]مصر',
    ],
    "gulf": [
        r'\b(شلونك|تمام|عليكم|والله|ماشاء الله|ياخي|الخير|طيب|أبشر|ماعليك|شسمه|هلا)\b',
        r'\b(تبي|بغيت|أبغى)\b',
        r'[ةه]سعود|[ةه]إمارات|[ةه]كويت|[ةه]قطر|[ةه]بحرين|[ةه]عمان',
    ],
    "levantine": [
        r'\b(كيفك|شو|هلا|والله|شغلة|كتير|حلو|قديش|ليش|بدي|عن جد|يعني|يا زلمة|هلأ)\b',
        r'\b(رح|عم)\b',
        r'[ةه]سور|[ةه]أردن|[ةه]لبنان|[ةه]فلسطين',
    ],
    "moroccan": [
        r'\b(لاباس|شنو|هاد|واخا|مزيان|بزاف|دابا|فين|علاش|كيفاش|نتا|نتي)\b',
        r'[ةه]مغرب',
    ],
}

# ─ـ ملفات تعريف الأسلوب حسب اللهجة ──────────────
DIALECT_PROFILES = {
    "egyptian":   {"warmth": 0.8, "directness": 0.7, "humor": 0.6, "formality": 0.3},
    "gulf":       {"warmth": 0.6, "directness": 0.8, "humor": 0.3, "formality": 0.8},
    "levantine":  {"warmth": 0.7, "directness": 0.7, "humor": 0.5, "formality": 0.5},
    "moroccan":   {"warmth": 0.6, "directness": 0.6, "humor": 0.4, "formality": 0.6},
    "modern_arabic": {"warmth": 0.5, "directness": 0.9, "humor": 0.3, "formality": 0.7},
    "english":    {"warmth": 0.6, "directness": 0.8, "humor": 0.4, "formality": 0.5},
}

# توجيهات النموذج (خفيفة جداً)
DIALECT_GUIDANCE = {
    "egyptian":     "المستخدم يميل للهجة المصرية. تحدث بالعربية الواضحة. يمكنك إضافة بعض التعبيرات المصرية الطبيعية باعتدال. الأولوية للفهم والإجابة المفيدة.",
    "gulf":         "المستخدم يميل للهجة الخليجية. استخدم لغة عربية سهلة ومهذبة. يمكن إضافة بعض المفردات الخليجية بشكل طبيعي. لا تجعل الأسلوب يطغى على المعلومة.",
    "levantine":    "المستخدم يميل للهجة الشامية. تحدث بأسلوب دافئ وطبيعي. اسمح ببعض المفردات الشامية عند الحاجة. الأولوية للوضوح والفائدة.",
    "moroccan":     "المستخدم يميل للهجة المغربية. حافظ على العربية المفهومة للجميع. استخدم تعابير مغربية خفيفة فقط إذا كانت مناسبة.",
    "modern_arabic": "تحدث بالعربية الفصحى البسيطة والواضحة. كن دافئاً ومهماً.",
    "english":       "Use natural modern English. Be warm and conversational. Prioritize clarity and usefulness.",
}

# ذاكرة مؤقتة لتفضيلات المستخدم
_user_dialect_prefs: Dict[str, Dict] = {}

def get_dialect_for_user(country_code: str = "SA", message: str = "") -> Tuple[str, float]:
    if not message or len(message.strip()) < 5:
        return "modern_arabic", 0.0

    message_lower = message.lower()
    scores = {}
    for dialect, patterns in DIALECT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, message_lower)
            score += len(matches)
        if score > 0:
            scores[dialect] = score

    if scores:
        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = min(scores[best] / total, 1.0) if total > 0 else 0.0
        return best, confidence
    return "modern_arabic", 0.0

def get_dialect_prompt(dialect: str) -> str:
    return DIALECT_GUIDANCE.get(dialect, DIALECT_GUIDANCE["modern_arabic"])

def get_dialect_profile(dialect: str) -> Dict[str, float]:
    return DIALECT_PROFILES.get(dialect, DIALECT_PROFILES["modern_arabic"])

def set_user_preferred_dialect(user_id: str, dialect: str):
    _user_dialect_prefs[user_id] = dialect

def get_user_preferred_dialect(user_id: str) -> Optional[str]:
    return _user_dialect_prefs.get(user_id)

print("✅ Dialect Service v3.0 migrated")
