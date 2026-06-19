"""
MyTwin – STT Service v3.0 (Vosk أساسي + Whisper Small اختياري)
- Vosk: خفيف، يعمل على Railway المجاني، بدون إنترنت.
- Whisper Small: اختياري، دقة عالية، يعمل محلياً عند الطلب فقط.
"""
import os, logging, asyncio, tempfile, base64
from typing import Optional

logger = logging.getLogger("stt_service")

# متغيرات كسولة
_whisper_model = None
_vosk_model = None

def _get_whisper():
    """تحميل كسول لـ Whisper فقط إذا كان الطلب يستدعيه."""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            size = os.getenv("WHISPER_MODEL_SIZE", "small")  # افتراضي small
            logger.info(f"⏳ تحميل Whisper {size}... (لن يعمل على Railway المجاني)")
            _whisper_model = whisper.load_model(size)
            logger.info(f"✅ Whisper {size} جاهز")
        except Exception as e:
            logger.warning(f"Whisper غير متاح (تأكد من تثبيته): {e}")
    return _whisper_model

def _get_vosk():
    """تحميل كسول لـ Vosk."""
    global _vosk_model
    if _vosk_model is None:
        try:
            import vosk
            model_path = os.getenv("VOSK_MODEL_PATH", "vosk-model-ar-0.22")
            if os.path.exists(model_path):
                _vosk_model = vosk.Model(model_path)
                logger.info("✅ Vosk جاهز (الأساسي)")
            else:
                logger.warning(f"Vosk model not found at {model_path}")
        except Exception as e:
            logger.warning(f"Vosk غير متاح: {e}")
    return _vosk_model

async def transcribe_audio(audio_base64: str, language: str = "ar", force_whisper: bool = False) -> Optional[str]:
    """
    تحويل الصوت إلى نص.
    - force_whisper: إذا كان True، يجرب Whisper أولاً (للاستخدام المحلي فقط).
    - دائماً يعود إلى Vosk كخط دفاع أول على الخادم.
    """
    
    # 1. إذا طلب المستخدم Whisper (للاستخدام المحلي أو الخوادم القوية)
    if force_whisper:
        whisper = _get_whisper()
        if whisper:
            try:
                text = await _whisper_transcribe(whisper, audio_base64, language)
                if text: return text
            except Exception as e:
                logger.warning(f"Whisper فشل: {e}")

    # 2. Vosk (الأساسي والخفيض)
    vosk = _get_vosk()
    if vosk:
        try:
            text = await _vosk_transcribe(vosk, audio_base64)
            if text: return text
        except Exception as e:
            logger.warning(f"Vosk فشل: {e}")

    # 3. تجربة Whisper كملاذ أخير إذا كان Vosk غير متوفر
    if not force_whisper:
        whisper = _get_whisper()
        if whisper:
            try:
                text = await _whisper_transcribe(whisper, audio_base64, language)
                if text: return text
            except Exception as e:
                logger.warning(f"Whisper (fallback) فشل: {e}")

    return None

async def _whisper_transcribe(model, audio_base64: str, language: str) -> Optional[str]:
    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        loop = asyncio.get_running_loop()
        lang = None if language == "auto" else language
        result = await loop.run_in_executor(None, lambda: model.transcribe(tmp_path, language=lang, fp16=False))
        return result.get("text", "").strip()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

async def _vosk_transcribe(model, audio_base64: str) -> Optional[str]:
    try:
        import vosk, json
        audio_bytes = base64.b64decode(audio_base64)
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(audio_bytes)
        result = json.loads(rec.FinalResult())
        return result.get("text", "").strip()
    except:
        return None
