"""
MyTwin – Intent Engine v2.1 (Production Ready)
- Regex دقيق يدعم العربية والإنجليزية
- نظام Scoring متوازن للرسائل القصيرة والطويلة
- Memory Boost للأسئلة عن الذكريات
- أسماء نوايا موحدة مع باقي النظام
"""
import logging, re
from typing import Dict, Any, Optional

logger = logging.getLogger("intent_engine")

INTENT_RULES = {
    "emotional": {
        "keywords": [
            "حزين", "خايف", "مكتئب", "قلق", "محتار", "زعلان", "متضايق",
            "مخنوق", "زهقان", "مش طايق", "تعبان نفسيا",
            "ضايقة", "مضغوط", "مقهور",
            "sad", "scared", "depressed", "anxious", "lonely", "worried", "stressed", "overwhelmed"
        ],
        "weight": 1.5,
        "emotion_boost": ["sadness", "fear", "anger"]
    },
    "coaching": {
        "keywords": [
            "نصيحة", "نصائح", "أرشدني", "وجهني", "طور نفسي", "ساعدني",
            "advice", "guide", "help me improve", "self-improvement", "growth"
        ],
        "weight": 1.3,
        "emotion_boost": []
    },
    "decision": {
        "keywords": [
            "قرار", "خيارات", "أختار", "محتار بين", "شور علي", "رأيك",
            "decision", "choose", "options", "what should I do", "help me decide"
        ],
        "weight": 1.4,
        "emotion_boost": ["fear", "anxiety"]
    },
    "career": {
        "keywords": [
            "وظيفة", "شغل", "عمل", "راتب", "ترقية", "مقابلة", "سيرة ذاتية", "مهنة",
            "job", "career", "salary", "promotion", "interview", "cv", "resume", "work"
        ],
        "weight": 1.2,
        "emotion_boost": []
    },
    "coding": {
        "keywords": [
            "كود", "برمجة", "بايثون", "جافا", "تطبيق", "خطأ برمجي", "algorithm",
            "code", "python", "javascript", "react", "bug", "debug", "function"
        ],
        "weight": 1.1,
        "emotion_boost": []
    },
    "greeting": {
        "keywords": ["مرحبا", "اهلا", "صباح الخير", "مساء الخير", "هاي", "السلام عليكم", "hello", "hi", "hey"],
        "weight": 0.5,
        "emotion_boost": []
    },
    "goodbye": {
        "keywords": ["مع السلامة", "باي", "سلام", "bye", "goodbye", "إلى اللقاء"],
        "weight": 0.8,
        "emotion_boost": []
    },
    "gratitude": {
        "keywords": ["شكرا", "تسلم", "ممنون", "thanks", "thank you", "appreciate"],
        "weight": 0.8,
        "emotion_boost": []
    },
    "weather": {
        "keywords": ["طقس", "جو", "حرارة", "مطر", "شمس", "weather", "rain", "sunny", "temperature"],
        "weight": 1.0,
        "emotion_boost": []
    },
    "music": {
        "keywords": ["أغنية", "موسيقى", "اسمع", "شغل", "song", "music", "playlist"],
        "weight": 1.0,
        "emotion_boost": []
    },
    "news": {
        "keywords": ["أخبار", "حدث", "حصل", "news", "headlines"],
        "weight": 1.0,
        "emotion_boost": []
    },
    "memory": {
        "keywords": ["ذكرت", "قلت", "اتذكر", "remember", "memory", "سابق"],
        "weight": 1.2,
        "emotion_boost": []
    },
    "goal": {
        "keywords": ["هدف", "أخطط", "نفسي أحقق", "عايز أوصل", "goal", "plan", "achieve"],
        "weight": 1.2,
        "emotion_boost": []
    },
    "search": {
        "keywords": ["بحث", "search", "google", "معلومات عن", "اعرف"],
        "weight": 1.0,
        "emotion_boost": []
    },
    "shopping": {
        "keywords": ["اشتري", "شراء", "سعر", "منتج", "buy", "purchase", "price", "product"],
        "weight": 1.0,
        "emotion_boost": []
    },
    "planning": {
        "keywords": ["خطة", "تنظيم", "جدول", "مواعيد", "schedule", "organize", "timeline"],
        "weight": 1.1,
        "emotion_boost": []
    },
}

class IntentEngine:
    def detect(self, message: str, lang: str = "ar", emotion: Optional[str] = None) -> Dict[str, Any]:
        if not message:
            return {"primary": "general", "confidence": 0.0, "secondary": [], "all_scores": {}}

        text = message.lower().strip()
        scores = {}
        
        for intent, config in INTENT_RULES.items():
            score = 0.0
            for kw in config["keywords"]:
                pattern = rf'(?<!\S){re.escape(kw)}(?!\S)'
                if re.search(pattern, text):
                    score += 1.0
            if score > 0:
                score = score * config["weight"]
                scores[intent] = score

        if re.search(r'(?<!\S)(?:اتذكر|ذكرت|remember|memory)(?!\S)', text):
            scores["memory"] = scores.get("memory", 0) + 0.4

        if emotion:
            for intent, config in INTENT_RULES.items():
                if emotion in config.get("emotion_boost", []):
                    scores[intent] = scores.get(intent, 0) + 0.25

        word_count = len(text.split())
        max_possible = max(3, min(10, word_count * 0.5))
        for intent in scores:
            scores[intent] = min(scores[intent] / max_possible, 1.0)

        if not scores:
            return {"primary": "general", "confidence": 0.0, "secondary": [], "all_scores": {}}

        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_intents[0][0]
        confidence = sorted_intents[0][1]
        secondary = [(i, s) for i, s in sorted_intents[1:4] if s > 0.2]

        return {
            "primary": primary,
            "confidence": round(confidence, 2),
            "secondary": secondary,
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }

intent_engine = IntentEngine()
