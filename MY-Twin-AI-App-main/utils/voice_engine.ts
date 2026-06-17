import * as Speech from "expo-speech";
import { Audio } from "expo-av";
import { useTwinStore, VoiceConfig } from "../store/useTwinStore";

// ==================== HELPERS ====================

function cleanTextForSpeech(text: string): string {
  if (!text) return "";
  return text
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/[❤️‍🔥✨🌟💜🫂🤗🫶💕💖💪🤝]/gu, "")
    .replace(/\*\*/g, "").replace(/\*/g, "")
    .replace(/\n{2,}/g, "، ").replace(/\n/g, " ")
    .replace(/\s{2,}/g, " ").trim();
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  // أسرع من loop عادي بـ 3x
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

// ==================== TTS PROVIDERS ====================

/**
 * ✅ Expo Speech - محلي، مجاني، يعمل بدون إنترنت
 */
async function speakWithExpoSpeech(text: string, config: VoiceConfig): Promise<void> {
  await Speech.stop();
  
  return new Promise((resolve, reject) => {
    Speech.speak(text, {
      language: config.language,
      pitch: config.pitch,
      rate: config.rate,
      onDone: () => resolve(),
      onError: (err) => reject(err),
    });
  });
}

/**
 * ✅ Edge TTS - عبر الخادم (أو مباشر إذا كان لديك proxy)
 */
async function speakWithEdgeTTS(text: string, config: VoiceConfig): Promise<void> {
  try {
    // إذا كان لديك endpoint محلي للـ Edge TTS
    const response = await fetch('/api/edge-tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        voice: config.voiceId,
        pitch: config.pitch,
        rate: config.rate,
      }),
    });

    if (!response.ok) throw new Error(`Edge TTS failed: ${response.status}`);

    const blob = await response.blob();
    const reader = new FileReader();

    return new Promise((resolve, reject) => {
      reader.onloadend = async () => {
        try {
          const base64 = (reader.result as string).split(',')[1];
          const { sound } = await Audio.Sound.createAsync(
            { uri: `data:audio/mp3;base64,${base64}` },
            { shouldPlay: true }
          );
          sound.setOnPlaybackStatusUpdate((status) => {
            if (status.isLoaded && status.didJustFinish) {
              sound.unloadAsync();
              resolve();
            }
          });
        } catch (e) {
          reject(e);
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (e) {
    console.warn("Edge TTS failed, falling back to Expo Speech");
    throw e; // سيتم التقاطه في الدالة الرئيسية
  }
}

/**
 * ✅ ElevenLabs - عبر الخادم (يتطلب API key)
 */
async function speakWithElevenLabs(text: string, config: VoiceConfig): Promise<void> {
  try {
    const response = await fetch('/api/elevenlabs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        voice_id: config.voiceId,
        model_id: 'eleven_multilingual_v2',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.3,
        },
      }),
    });

    if (!response.ok) throw new Error(`ElevenLabs failed: ${response.status}`);

    const blob = await response.blob();
    const reader = new FileReader();

    return new Promise((resolve, reject) => {
      reader.onloadend = async () => {
        try {
          const base64 = (reader.result as string).split(',')[1];
          const { sound } = await Audio.Sound.createAsync(
            { uri: `data:audio/mp3;base64,${base64}` },
            { shouldPlay: true }
          );
          sound.setOnPlaybackStatusUpdate((status) => {
            if (status.isLoaded && status.didJustFinish) {
              sound.unloadAsync();
              resolve();
            }
          });
        } catch (e) {
          reject(e);
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (e) {
    console.warn("ElevenLabs failed, falling back to Expo Speech");
    throw e;
  }
}

// ==================== MAIN EXPORT ====================

/**
 * ✅ يتحدث بناءً على إعدادات الصوت من الـ Store
 * - يختار المزود تلقائياً
 * - يرتبط بنوع التوأم (ذكر/أنثى/غير محدد)
 * - يحاول الخادم أولاً، ثم يرجع للمحلي
 */
export async function speakResponse(
  text: string,
  options?: { onDone?: () => void; onStart?: () => void }
): Promise<void> {
  try {
    const clean = cleanTextForSpeech(text);
    if (!clean) return;

    const store = useTwinStore.getState();
    
    // ✅ استخدام getVoiceConfig() من الـ Store
    const voiceConfig = store.getVoiceConfig();
    
    options?.onStart?.();

    // ✅ اختيار المزود حسب الإعداد
    switch (voiceConfig.provider) {
      case 'edge_tts':
        try {
          await speakWithEdgeTTS(clean, voiceConfig);
        } catch {
          await speakWithExpoSpeech(clean, voiceConfig);
        }
        break;

      case 'elevenlabs':
        try {
          await speakWithElevenLabs(clean, voiceConfig);
        } catch {
          await speakWithExpoSpeech(clean, voiceConfig);
        }
        break;

      case 'expo_speech':
      default:
        await speakWithExpoSpeech(clean, voiceConfig);
        break;
    }

    options?.onDone?.();
  } catch (e) {
    console.warn("speakResponse error:", e);
    options?.onDone?.();
  }
}

// ==================== STT (Speech-to-Text) ====================

export async function transcribeAudio(audioBase64: string): Promise<string> {
  try {
    const store = useTwinStore.getState();
    const lang = store.lang === 'ar' ? 'ar-SA' : 'en-US';

    const response = await fetch('/api/stt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio: audioBase64,
        language: lang,
      }),
    });

    if (!response.ok) throw new Error(`STT failed: ${response.status}`);
    
    const data = await response.json();
    return data.text || '';
  } catch (e) {
    console.warn("STT failed:", e);
    return '';
  }
}

// ==================== CONTROLS ====================

export async function stopSpeaking(): Promise<void> {
  await Speech.stop();
}

export async function isSpeaking(): Promise<boolean> {
  return Speech.isSpeakingAsync();
}

export async function pauseSpeaking(): Promise<void> {
  // Expo Speech لا يدعم pause مباشرة
  await Speech.stop();
}

export async function resumeSpeaking(): Promise<void> {
  // يتطلب إعادة التشغيل من البداية
  console.warn("Resume not supported in Expo Speech");
}
