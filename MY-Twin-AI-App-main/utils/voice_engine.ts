import * as Speech from "expo-speech";
import { useTwinStore } from "../store/useTwinStore";
import { API } from "../lib/api";

const GENDER_VOICES: Record<string, string> = {
  male: 'ar-SA-HamedNeural',
  female: 'ar-SA-ZariyahNeural',
};

function cleanTextForSpeech(text: string): string {
  if (!text) return "";
  return text
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/[❤️‍🔥✨🌟💜🫂🤗🫶💕💖💪🤝]/gu, "")
    .replace(/\*\*/g, "").replace(/\*/g, "")
    .replace(/\n{2,}/g, "، ").replace(/\n/g, " ")
    .replace(/\s{2,}/g, " ").trim();
}

export async function speakResponse(text: string, options?: any): Promise<void> {
  try {
    const clean = cleanTextForSpeech(text);
    if (!clean) return;

    const store = useTwinStore.getState();
    const twinGender = store.twinGender || 'female';
    const tier = store.tier || 'free';

    // للباقات المدفوعة: نستخدم السيرفر مباشرة
    if (tier && ['premium', 'pro', 'yearly'].includes(tier)) {
      try {
        await API.post('/api/voice/speak', { text: clean, tier, gender: twinGender, emotion: options?.emotion || 'neutral' });
        return;
      } catch (e) {
        console.warn("Server voice failed, falling back to local TTS");
      }
    }

    // للباقات المجانية: نجرب السيرفر أولاً (Edge TTS)، وإذا فشل نستخدم expo-speech المحلي
    try {
      await API.post('/api/voice/speak', { text: clean, tier: 'free', gender: twinGender, emotion: options?.emotion || 'neutral' });
      return;
    } catch (e) {
      // Fallback إلى expo-speech المحلي
      const defaultVoice = GENDER_VOICES[twinGender] || GENDER_VOICES.female;
      await Speech.stop();
      Speech.speak(clean, {
        language: "ar-SA",
        pitch: options?.pitch || 1.0,
        rate: options?.rate || 0.9,
        voice: defaultVoice,
        onError: (err: any) => console.warn("TTS fallback error:", err),
      });
    }
  } catch (e) {
    console.warn("speakResponse fatal error:", e);
  }
}

export function stopSpeaking(): void { Speech.stop(); }
export function isSpeaking(): Promise<boolean> { return Speech.isSpeakingAsync(); }
