import * as Speech from "expo-speech";
import { useTwinStore } from "../store/useTwinStore";
import { API } from "../lib/api";

export interface VoiceOptions {
  pitch?: number;
  rate?: number;
  language?: string;
  onDone?: () => void;
  emotion?: string;
  intensity?: number;
  personality?: string;
}

const EMOTION_PRESETS: Record<string, { pitch: number; rate: number }> = {
  joy: { pitch: 1.15, rate: 0.95 },
  sadness: { pitch: 0.85, rate: 0.75 },
  anger: { pitch: 1.0, rate: 1.0 },
  fear: { pitch: 0.9, rate: 0.85 },
  love: { pitch: 1.05, rate: 0.85 },
  surprise: { pitch: 1.2, rate: 1.0 },
  neutral: { pitch: 1.0, rate: 0.9 },
};

const GENDER_VOICES: Record<string, string> = {
  male: 'ar-SA-HamedNeural',
  female: 'ar-SA-ZariyahNeural',
};

function cleanTextForSpeech(text: string): string {
  if (!text) return "";
  return text
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/[❤️‍🔥✨🌟💜🫂🤗🫶💕💖💪🤝]/gu, "")
    .replace(/\*\*/g, "")
    .replace(/\*/g, "")
    .replace(/\n{2,}/g, "، ")
    .replace(/\n/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

export async function speakResponse(text: string, options?: VoiceOptions): Promise<void> {
  try {
    const clean = cleanTextForSpeech(text);
    if (!clean) return;

    const store = useTwinStore.getState();
    const twinGender = store.twinGender || 'female';
    const tier = store.tier || 'free';
    const emotion = options?.emotion || 'neutral';

    // تحديد ما إذا كنا نستخدم الخادم (للباقات المميزة)
    const useServerVoice = ['premium', 'pro', 'yearly'].includes(tier);

    if (useServerVoice) {
      // إرسال طلب الصوت إلى الخادم مع الجنس والعاطفة
      try {
        const response = await API.post('/api/voice/speak', {
          text: clean,
          tier,
          gender: twinGender,
          emotion,
        }, { responseType: 'arraybuffer' });
        // يمكن تشغيل الصوت المستلم عبر expo-av (غير مطبق هنا حفاظاً على البساطة)
        // للمثال سنستمر مع expo-speech
      } catch (e) {
        console.warn("Server voice failed, falling back to local TTS");
      }
    }

    // استخدام expo-speech كطبقة أساسية أو احتياطية
    const defaultVoice = GENDER_VOICES[twinGender] || GENDER_VOICES.female;
    let pitch = options?.pitch ?? 1.0;
    let rate = options?.rate ?? 0.9;

    if (emotion && EMOTION_PRESETS[emotion]) {
      const preset = EMOTION_PRESETS[emotion];
      pitch = preset.pitch;
      rate = preset.rate;
    }

    await Speech.stop();
    Speech.speak(clean, {
      language: "ar-SA",
      pitch,
      rate,
      voice: defaultVoice,
      onDone: () => {
        if (options?.onDone) options.onDone();
      },
      onError: (e) => {
        console.warn("TTS error:", e);
      },
    });
  } catch (e) {
    console.warn("speakResponse error:", e);
  }
}

export function stopSpeaking(): void {
  Speech.stop();
}

export function isSpeaking(): Promise<boolean> {
  return Speech.isSpeakingAsync();
}
