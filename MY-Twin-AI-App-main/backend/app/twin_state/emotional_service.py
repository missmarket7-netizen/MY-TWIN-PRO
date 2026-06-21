"""
Emotional Service v3.0 – متكامل مع TCMA Emotional Engine
=============================================================
يستخدم TCMA (المحرك العربي العميق) كخيار أول.
يعود للمحرك المحلي (Lexicon/Negation/Intensity) كاحتياطي.
"""
import logging, re, hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("emotional_service")

try:
    from app.memory.emotional.emotional_memory import analyze_arabic_context, store_emotional_memory
    TCMA_EMOTION_AVAILABLE = True
except ImportError:
    TCMA_EMOTION_AVAILABLE = False

try:
    from app.infrastructure.cache.cache_service import get as cache_get, set as cache_set
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

class EmotionalService:
    LEXICON = {
        "joy": {
            "ar": ["سعيد","فرح","مبسوط","ممتاز","رائع","جميل","بضحك","ههه","😂","😊","متحمس","فخور","الحمدلله"],
            "en": ["happy","joy","glad","great","wonderful","lol","😂","excited","proud","yay"]
        },
        "sadness": {
            "ar": ["حزين","مؤلم","بكي","زعلان","متضايق","💔","😢","😔","مكتئب","وحيد","فقدت"],
            "en": ["sad","pain","cry","upset","heartbroken","💔","😢","depressed","lonely","lost"]
        },
        "anger": {
            "ar": ["غاضب","محبط","غضب","🔥","😡","سخيف","لا أحتمل","كفى"],
            "en": ["angry","mad","furious","🔥","😡","hate","enough","stupid"]
        },
        "fear": {
            "ar": ["خائف","قلق","خوف","مرعوب","متوتر","😨","😰"],
            "en": ["scared","afraid","fear","anxious","worried","nervous","😨","panic"]
        },
        "love": {
            "ar": ["أحبك","حبيب","قلبي","💕","💖","عشق","حنية"],
            "en": ["love","dear","sweetheart","💕","💖","adore","miss you"]
        },
        "surprise": {
            "ar": ["مفاجأة","عجيب","😮","😲","لا أصدق","غريب"],
            "en": ["surprise","wow","😮","😲","unbelievable","strange"]
        },
    }

    HIGH_RISK_PHRASES = [
        "عايز أموت","أنا مش عايز أعيش","بفكر في الانتحار","مافيش أمل",
        "i want to die","i don't want to live","suicide","no hope"
    ]

    def _analyze_local(self, text: str) -> Dict[str, Any]:
        """المحرك المحلي (احتياطي)"""
        lang = "ar" if len(re.findall(r'[\u0600-\u06FF]', text)) > len(text) * 0.3 else "en"
        text_lower = text.lower().strip()

        scores = {}
        for emotion, words_dict in self.LEXICON.items():
            score = sum(1 for w in words_dict.get(lang, []) if w.lower() in text_lower)
            if score > 0:
                scores[emotion] = score

        if scores:
            sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_emotions[0][0]
            secondary = sorted_emotions[1][0] if len(sorted_emotions) > 1 else "neutral"
        else:
            primary = "neutral"
            secondary = "neutral"

        intensity = 0.5
        for word in ["جداً","كثير","للغاية","very","extremely","really"]:
            if word.lower() in text_lower:
                intensity += 0.15

        return {
            "primary": primary,
            "secondary": secondary,
            "intensity": min(intensity, 1.0),
            "valence": 0.3 if primary in ["joy","love"] else -0.3 if primary in ["sadness","anger","fear"] else 0.0,
            "lang": lang,
            "method": "local"
        }

    async def analyze(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        if not text:
            return {"primary": "neutral", "secondary": "neutral", "intensity": 0.5, "needs_support": False}

        # 1. محاولة TCMA أولاً (المحرك العربي العميق)
        if TCMA_EMOTION_AVAILABLE:
            try:
                tcma_result = analyze_arabic_context(text)
                if tcma_result and tcma_result.get("confidence", 0) > 0.5:
                    result = {
                        "primary": tcma_result.get("real_emotion", "neutral"),
                        "secondary": "neutral",
                        "intensity": tcma_result.get("confidence", 0.5),
                        "valence": 0.2 if tcma_result.get("real_emotion") in ["joy","love"] else -0.2,
                        "confidence": tcma_result.get("confidence", 0),
                        "needs_support": tcma_result.get("real_emotion") in ["sadness","fear","anger"],
                        "cultural_analysis": tcma_result.get("cultural_analysis", ""),
                        "method": "tcma_arabic_engine"
                    }
                    if user_id:
                        try:
                            await store_emotional_memory(
                                user_id=user_id, expressed_text=text,
                                detected_emotion=result, trigger="chat"
                            )
                        except: pass
                    return result
            except Exception as e:
                logger.warning(f"TCMA emotion failed: {e}")

        # 2. احتياطي: المحرك المحلي
        result = self._analyze_local(text)

        # 3. فحص المخاطر
        text_lower = text.lower()
        result["risk_level"] = "high" if any(p in text_lower for p in self.HIGH_RISK_PHRASES) else "low"
        result["needs_support"] = result.get("primary") in ["sadness","fear","anger"] and result.get("intensity", 0) > 0.6

        return result

emotional_service = EmotionalService()
logger.info("✅ Emotional Service v3.0 initialized")
