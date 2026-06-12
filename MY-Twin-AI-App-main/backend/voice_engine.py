"""
MyTwin – Voice Engine v4.2 (توجيه ذكي للنطق مع دعم الجنس)
- يعتمد على expo-speech في الواجهة الأمامية للعامية
- يحتفظ بـ Edge TTS للغات المدعومة فقط (الإنجليزية، الفصحى)
- يوفر ElevenLabs للباقات المتميزة مع دعم أصوات متعددة
- تم الإصلاح: دعم الجنس (ذكر/أنثى) في جميع المزودين
"""
import os, logging, asyncio
from typing import Optional, Dict, Any
from enum import Enum
from voice_personality import get_voice_personality, GENDER_VOICE_MAPPING

logger = logging.getLogger(__name__)

class VoiceProvider(str, Enum):
    DISABLED = "disabled"
    EDGE = "edge"
    ELEVENLABS = "elevenlabs"
    SYSTEM = "system"  # توجيه إلى الواجهة

VOICE_CONFIG = {
    "free_trial_14d": {"provider": VoiceProvider.SYSTEM, "available": [VoiceProvider.SYSTEM]},
    "free":           {"provider": VoiceProvider.SYSTEM, "available": [VoiceProvider.SYSTEM]},
    "plus":           {"provider": VoiceProvider.SYSTEM, "available": [VoiceProvider.SYSTEM]},
    "premium_trial":  {"provider": VoiceProvider.SYSTEM, "available": [VoiceProvider.SYSTEM]},
    "premium":        {"provider": VoiceProvider.ELEVENLABS, "available": [VoiceProvider.SYSTEM, VoiceProvider.ELEVENLABS]},
    "pro":            {"provider": VoiceProvider.ELEVENLABS, "available": [VoiceProvider.SYSTEM, VoiceProvider.ELEVENLABS]},
    "yearly":         {"provider": VoiceProvider.ELEVENLABS, "available": [VoiceProvider.SYSTEM, VoiceProvider.ELEVENLABS]},
}

# تكوين ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# دعم أصوات متعددة لـ ElevenLabs
ELEVENLABS_VOICE_IDS = {
    "default": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    "male": os.getenv("ELEVENLABS_MALE_VOICE_ID", "male_voice_elevenlabs_id"),
    "female": os.getenv("ELEVENLABS_FEMALE_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
}

# تكوين Edge TTS للأصوات حسب الجنس
EDGE_VOICE_MAPPING = {
    "male": {
        "ar": "ar-SA-HamedNeural",      # عربي ذكر
        "en": "en-US-GuyNeural",         # إنجليزي ذكر
        "default": "en-US-GuyNeural"
    },
    "female": {
        "ar": "ar-SA-ZariyahNeural",     # عربي أنثى
        "en": "en-US-JennyNeural",       # إنجليزي أنثى
        "default": "en-US-JennyNeural"
    }
}

def get_voice_config(tier: str) -> Dict[str, Any]:
    """الحصول على إعدادات الصوت للباقة المحددة"""
    return VOICE_CONFIG.get(tier, {"provider": VoiceProvider.SYSTEM, "available": [VoiceProvider.SYSTEM]})

def get_elevenlabs_voice_id(gender: str = "female") -> str:
    """الحصول على معرف الصوت المناسب من ElevenLabs حسب الجنس"""
    return ELEVENLABS_VOICE_IDS.get(gender, ELEVENLABS_VOICE_IDS["default"])

def get_edge_voice(gender: str = "female", language: str = "ar") -> str:
    """الحصول على صوت Edge TTS المناسب حسب الجنس واللغة"""
    voice_map = EDGE_VOICE_MAPPING.get(gender, EDGE_VOICE_MAPPING["female"])
    return voice_map.get(language, voice_map["default"])

async def speakResponse(
    text: str,
    tier: str = "free",
    gender: str = "female",
    emotion: str = "neutral"
) -> Optional[bytes]:
    """
    تحويل النص إلى كلام.
    
    Args:
        text: النص المراد تحويله
        tier: الباقة (free, plus, premium, etc.)
        gender: الجنس (male, female)
        emotion: المشاعر (neutral, happy, sad, etc.)
    
    Returns:
        - None: للباقات المجانية (توجيه الواجهة لاستخدام expo-speech)
        - bytes: البيانات الصوتية للباقات المتميزة
    """
    if not text or not text.strip():
        return None

    config = get_voice_config(tier)
    provider = config["provider"]

    # التحقق من صحة الجنس
    if gender not in ["male", "female"]:
        logger.warning(f"جنس غير صالح: {gender}، استخدام الافتراضي female")
        gender = "female"

    # للباقات المجانية: إشارة للواجهة باستخدام TTS المحلي
    if provider == VoiceProvider.SYSTEM:
        return None

    # الحصول على شخصية الصوت مع دعم الجنس (تم الإصلاح)
    try:
        personality = get_voice_personality(emotion, gender)
    except Exception as e:
        logger.error(f"خطأ في get_voice_personality: {e}")
        personality = get_voice_personality("friend", gender)

    # ElevenLabs للباقات المتميزة
    if provider == VoiceProvider.ELEVENLABS and ELEVENLABS_API_KEY:
        voice_id = get_elevenlabs_voice_id(gender)
        logger.info(f"استخدام ElevenLabs - الجنس: {gender}, الصوت: {voice_id}")
        return await _elevenlabs_tts(text, personality, voice_id)

    # Edge TTS احتياطي (للإنجليزية / الفصحى فقط)
    if provider == VoiceProvider.EDGE:
        return await _edge_tts(text, personality, gender)

    return None

async def _edge_tts(text: str, personality: Dict[str, Any], gender: str = "female") -> Optional[bytes]:
    """
    تحويل النص إلى كلام باستخدام Edge TTS مع دعم الجنس
    
    Args:
        text: النص المراد تحويله
        personality: إعدادات الشخصية
        gender: الجنس (male/female)
    """
    try:
        import edge_tts
        
        # اختيار الصوت المناسب حسب الجنس
        voice = get_edge_voice(gender, "ar")
        
        # استخراج الإعدادات من الشخصية
        rate_str = f"{int((personality.get('rate', 1.0) - 1.0) * 100):+d}%"
        pitch_str = f"{int((personality.get('pitch', 1.0) - 1.0) * 50):+d}Hz"
        
        logger.info(f"Edge TTS - الصوت: {voice}, المعدل: {rate_str}, النغمة: {pitch_str}")
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
        audio_chunks = []
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        
        if audio_chunks:
            logger.info(f"✅ تم توليد {len(audio_chunks)} مقطع صوتي")
            return b"".join(audio_chunks)
        else:
            logger.warning("⚠️ لم يتم توليد أي صوت")
            return None
            
    except ImportError:
        logger.error("❌ مكتبة edge_tts غير مثبتة. استخدم: pip install edge-tts")
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في Edge TTS: {e}")
        return None

async def _elevenlabs_tts(text: str, personality: Dict[str, Any], voice_id: str) -> Optional[bytes]:
    """
    تحويل النص إلى كلام باستخدام ElevenLabs مع دعم الأصوات المتعددة
    
    Args:
        text: النص المراد تحويله
        personality: إعدادات الشخصية
        voice_id: معرف الصوت في ElevenLabs
    """
    if not ELEVENLABS_API_KEY:
        logger.error("❌ مفتاح ElevenLabs API غير موجود")
        return None
        
    try:
        import httpx
        
        # استخراج إعدادات الصوت من الشخصية
        stability = personality.get("stability", 0.5)
        similarity = personality.get("similarity_boost", 0.75)
        
        logger.info(f"ElevenLabs - الصوت: {voice_id}, الثبات: {stability}, التشابه: {similarity}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json={
                    "text": text,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity
                    },
                    "model_id": "eleven_multilingual_v2"
                },
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
            )
            
            if resp.status_code == 200:
                logger.info(f"✅ تم توليد الصوت بنجاح من ElevenLabs")
                return resp.content
            else:
                logger.warning(f"⚠️ خطأ ElevenLabs: {resp.status_code} - {resp.text}")
                return None
                
    except ImportError:
        logger.error("❌ مكتبة httpx غير مثبتة. استخدم: pip install httpx")
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في ElevenLabs: {e}")
        return None

def startRecordingVoice() -> bool:
    """بدء تسجيل الصوت"""
    logger.info("بدء تسجيل الصوت...")
    return True

async def stopRecordingVoice(audio_bytes: Optional[bytes] = None) -> Optional[str]:
    """إيقاف تسجيل الصوت وتحويله إلى نص"""
    # STT من خلال expo-speech أو Google Cloud
    logger.info("إيقاف تسجيل الصوت...")
    return None

class VoiceEngine:
    """محرك الصوت الرئيسي مع دعم كامل للجنس"""
    
    def __init__(self):
        self.enabled = True
        logger.info("✅ تهيئة Voice Engine v4.2")
        
    async def speak(self, text: str, tier: str = "free", emotion: str = "neutral", gender: str = "female") -> Optional[bytes]:
        """
        تحويل النص إلى كلام مع دعم الجنس
        
        Args:
            text: النص المراد نطقه
            tier: الباقة
            emotion: المشاعر
            gender: الجنس (male/female)
        """
        return await speakResponse(text, tier, gender, emotion)
    
    def get_available_voices(self) -> Dict[str, Any]:
        """الحصول على قائمة الأصوات المتاحة"""
        return {
            "elevenlabs": ELEVENLABS_VOICE_IDS,
            "edge": EDGE_VOICE_MAPPING,
            "genders": list(GENDER_VOICE_MAPPING.keys())
        }

# إنشاء نسخة عامة من محرك الصوت
voice_engine = VoiceEngine()

# اختبار سريع عند التشغيل المباشر
if __name__ == "__main__":
    print("✅ Voice Engine v4.2 (دعم كامل للجنس والأصوات المتعددة)")
    print("\n📊 إحصائيات النظام:")
    print(f"- الباقات المدعومة: {list(VOICE_CONFIG.keys())}")
    print(f"- الأصوات المتاحة: {list(ELEVENLABS_VOICE_IDS.keys())}")
    print(f"- الأجناس المدعومة: {list(GENDER_VOICE_MAPPING.keys())}")
    print(f"- Edge TTS: {list(EDGE_VOICE_MAPPING.keys())}")
    
    # اختبار سريع للدوال
    print("\n🧪 اختبار الدوال:")
    print(f"1. get_elevenlabs_voice_id('male'): {get_elevenlabs_voice_id('male')}")
    print(f"2. get_elevenlabs_voice_id('female'): {get_elevenlabs_voice_id('female')}")
    print(f"3. get_edge_voice('male', 'ar'): {get_edge_voice('male', 'ar')}")
    print(f"4. get_edge_voice('female', 'ar'): {get_edge_voice('female', 'ar')}")
    print(f"5. get_voice_config('premium'): {get_voice_config('premium')}")
    
    print("\n✨ جاهز للاستخدام!")
