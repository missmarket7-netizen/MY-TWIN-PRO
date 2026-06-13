"""
MyTwin – Emotional Engine v9.2 (مع تخزين متجه المشاعر الكامل والتفاصيل)
"""
import os, logging, re, hashlib, json, asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from cache import get as cache_get, set as cache_set
from supabase import create_client, Client

logger = logging.getLogger("emotional_engine")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class EmotionalStateTracker:
    LEXICON = {
        "joy": {
            "ar": ["سعيد", "فرح", "مبسوط", "ممتاز", "رائع", "جميل", "بضحك", "ههه", "😂", "😊", "😄", "💃", "🎉", "متحمس", "فخور", "الحمدلله"],
            "en": ["happy", "joy", "glad", "great", "wonderful", "lol", "😂", "😊", "😄", "excited", "proud", "yay"]
        },
        "sadness": {
            "ar": ["حزين", "مؤلم", "بكي", "زعلان", "متضايق", "يا حسرة", "💔", "😢", "😔", "مكتئب", "وحيد", "فقدت"],
            "en": ["sad", "pain", "cry", "upset", "heartbroken", "💔", "😢", "depressed", "lonely", "lost"]
        },
        "anger": {
            "ar": ["غاضب", "محبط", "غضب", "🔥", "😡", "🤬", "سخيف", "لا أحتمل", "كفى"],
            "en": ["angry", "mad", "furious", "🔥", "😡", "hate", "enough", "stupid"]
        },
        "fear": {
            "ar": ["خائف", "قلق", "خوف", "مرعوب", "متوتر", "😨", "😰", "لا أعرف ماذا سيحدث"],
            "en": ["scared", "afraid", "fear", "anxious", "worried", "nervous", "😨", "panic"]
        },
        "love": {
            "ar": ["أحبك", "حبيب", "قلبي", "💕", "💖", "🫶", "عشق", "حنية"],
            "en": ["love", "dear", "sweetheart", "💕", "💖", "adore", "miss you"]
        },
        "surprise": {
            "ar": ["مفاجأة", "عجيب", "😮", "😲", "لا أصدق", "غريب"],
            "en": ["surprise", "wow", "😮", "😲", "unbelievable", "strange"]
        },
        "disgust": {
            "ar": ["مقرف", "اشمئزاز", "يع", "🤢", "🤮", "قذر"],
            "en": ["disgust", "gross", "yuck", "🤢", "🤮", "dirty"]
        },
        "neutral": {
            "ar": ["طبيعي", "عادي", "تمام", "ليس سيئاً", "لا بأس"],
            "en": ["okay", "fine", "normal", "not bad", "alright"]
        }
    }

    NEGATION_WORDS = {
        "ar": ["لا", "ليس", "مش", "ما", "غير", "لم"],
        "en": ["not", "no", "don't", "isn't", "never", "neither"]
    }

    INTENSIFIERS = {
        "ar": {"جداً": 0.2, "كثير": 0.15, "للغاية": 0.25, "!!!": 0.2, "!": 0.1},
        "en": {"very": 0.2, "so": 0.15, "extremely": 0.25, "really": 0.18, "!!!": 0.2, "!": 0.1}
    }

    HIGH_RISK_PHRASES = [
        "عايز أموت", "أنا مش عايز أعيش", "بفكر في الانتحار", "مافيش أمل", "أنا بموت",
        "i want to die", "i don't want to live", "suicide", "no hope"
    ]
    MEDIUM_RISK_PHRASES = [
        "أنا متعب نفسياً", "مش قادر أكمل", "ببكي كل يوم", "تايه", "وحيد جداً",
        "i can't go on", "crying every day", "so lonely"
    ]

    def __init__(self):
        self.multi_client = None

    def _get_multi_client(self):
        if self.multi_client is None:
            try:
                from multi_ai import MultiAIClient
                self.multi_client = MultiAIClient()
            except:
                pass
        return self.multi_client

    def _detect_language(self, text: str) -> str:
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        return "ar" if len(arabic_chars) > len(text) * 0.3 else "en"

    def _analyze_local_deep(self, text: str) -> Dict[str, Any]:
        lang = self._detect_language(text)
        text_lower = text.lower().strip()

        emotion_scores = {}
        for emotion, words_dict in self.LEXICON.items():
            words = words_dict.get(lang, [])
            score = 0
            for word in words:
                if word.lower() in text_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score

        # النفي مع هروب الكلمات
        for emotion in list(emotion_scores.keys()):
            for neg_word in self.NEGATION_WORDS.get(lang, []):
                escaped_words = "|".join(re.escape(w) for w in self.LEXICON[emotion][lang][:5])
                pattern = rf'{re.escape(neg_word)}\s+\w*\s*({escaped_words})'
                if re.search(pattern, text_lower):
                    emotion_scores[emotion] = max(0, emotion_scores[emotion] - 2)
                    if emotion == "sadness":
                        emotion_scores["joy"] = emotion_scores.get("joy", 0) + 1
                    elif emotion == "joy":
                        emotion_scores["sadness"] = emotion_scores.get("sadness", 0) + 1

        intensity = 0.5
        for word, boost in self.INTENSIFIERS.get(lang, {}).items():
            if word.lower() in text_lower:
                intensity += boost

        positive = {"joy", "love", "surprise"}
        negative = {"sadness", "anger", "fear", "disgust"}
        pos_score = sum(v for k, v in emotion_scores.items() if k in positive)
        neg_score = sum(v for k, v in emotion_scores.items() if k in negative)
        total = pos_score + neg_score
        valence = (pos_score - neg_score) / max(total, 1)
        arousal = min(intensity, 1.0)

        if emotion_scores:
            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_emotions[0][0]
            secondary = sorted_emotions[1][0] if len(sorted_emotions) > 1 else "neutral"
            needs_support = primary in ["sadness", "fear", "anger", "disgust"] and intensity > 0.5
        else:
            primary = "neutral"
            secondary = "neutral"
            needs_support = False

        vector = {e: 0.0 for e in self.LEXICON}
        max_score = max(emotion_scores.values()) if emotion_scores else 1
        for e in emotion_scores:
            vector[e] = round(emotion_scores[e] / max_score, 2)

        return {
            "primary": primary,
            "secondary": secondary,
            "emotion_vector": vector,
            "intensity": min(intensity, 1.0),
            "valence": valence,
            "arousal": arousal,
            "needs_support": needs_support,
            "lang": lang
        }

    async def _detect_triggers(self, text: str, user_id: Optional[str] = None) -> Optional[str]:
        if len(text) < 50:
            return None
        client = self._get_multi_client()
        if not client:
            return None
        try:
            prompt = f"""استخرج سبب المشاعر من هذه الرسالة، وأعد كلمة واحدة أو اثنتين فقط:
الرسالة: "{text}"
السبب:"""
            result = await client.get_best_reply(prompt, task="deep_reasoning")
            return result.strip() if result else None
        except:
            return None

    async def _compute_trend(self, user_id: str, current_valence: float) -> str:
        if not db:
            return "stable"
        try:
            res = db.table("emotional_timeline").select("valence").eq("user_id", user_id)\
                    .order("created_at", desc=True).limit(5).execute()
            if not res.data or len(res.data) < 2:
                return "stable"
            valences = [r["valence"] for r in res.data][::-1]
            if valences[-1] - valences[0] > 0.2:
                return "improving"
            elif valences[-1] - valences[0] < -0.2:
                return "worsening"
            return "stable"
        except:
            return "stable"

    def _assess_risk(self, text: str, emotion: Dict[str, Any]) -> str:
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in self.HIGH_RISK_PHRASES):
            return "high"
        if any(phrase in text_lower for phrase in self.MEDIUM_RISK_PHRASES):
            return "medium"
        if emotion.get("primary") == "sadness" and emotion.get("intensity", 0) > 0.8:
            return "medium"
        return "low"

    async def analyze(self, text: str, gemini_key: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        if not text:
            return {"primary": "neutral", "secondary": "neutral", "intensity": 0.5, "needs_support": False}

        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"emotion:{text_hash}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        result = self._analyze_local_deep(text)

        if result["intensity"] < 0.4 and result["primary"] == "neutral":
            client = self._get_multi_client()
            if client:
                try:
                    prompt = f"""Analyze this message emotionally. Return ONLY JSON:
{{"primary":"...", "secondary":"...", "intensity":0.5, "valence":0.0, "needs_support":false}}
Message: "{text}"
JSON:"""
                    full_reply = await client.get_best_reply(prompt, task="emotional")
                    json_match = re.search(r'\{[^}]+\}', full_reply)
                    if json_match:
                        model_result = json.loads(json_match.group())
                        result.update(model_result)
                except Exception as e:
                    logger.warning(f"Emotion backup model failed: {e}")

        # حساب البيانات الإضافية
        trigger = None
        trend = "stable"
        mood = result["primary"]
        risk_level = "low"

        if user_id and db:
            try:
                trend = await self._compute_trend(user_id, result["valence"])
                trigger = await self._detect_triggers(text, user_id)
                mood = await self._get_mood(user_id)
                risk_level = self._assess_risk(text, result)

                # تخزين جميع البيانات في الجدول العاطفي
                db.table("emotional_timeline").insert({
                    "user_id": user_id,
                    "primary_emotion": result["primary"],
                    "secondary_emotion": result["secondary"],
                    "intensity": result["intensity"],
                    "valence": result["valence"],
                    "arousal": result["arousal"],
                    "emotion_vector": json.dumps(result["emotion_vector"]),
                    "trigger": trigger,
                    "trend": trend,
                    "mood": mood,
                    "risk_level": risk_level,
                    "needs_support": result["needs_support"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to store emotional timeline: {e}")

            result["trend"] = trend
            result["trigger"] = trigger
            result["mood"] = mood
            result["risk_level"] = risk_level
        else:
            result["trend"] = "stable"
            result["trigger"] = None
            result["mood"] = result["primary"]
            result["risk_level"] = self._assess_risk(text, result)

        cache_set(cache_key, result, 600)
        return result

    async def _get_mood(self, user_id: str) -> str:
        if not db:
            return "neutral"
        try:
            res = db.table("emotional_timeline").select("primary_emotion").eq("user_id", user_id)\
                    .order("created_at", desc=True).limit(10).execute()
            if not res.data:
                return "neutral"
            freq = {}
            for r in res.data:
                e = r["primary_emotion"]
                freq[e] = freq.get(e, 0) + 1
            return max(freq, key=freq.get)
        except:
            return "neutral"


emotional_tracker = EmotionalStateTracker()
print("✅ Emotional Engine v9.2 (with full emotion vector storage) initialized")
