import * as Speech from "expo-speech";
import { useTwinStore } from "../store/useTwinStore";
import { API } from "../lib/api";

// ==================== TYPES ====================

interface VoiceOption {
  identifier: string;
  name: string;
  language: string;
  gender: 'male' | 'female' | 'unknown';
  quality: number;
}

// ==================== VOICE MAPS ====================

const GENDER_VOICES: Record<string, string> = {
  male: 'ar-SA-HamedNeural',
  female: 'ar-SA-ZariyahNeural',
};

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
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

// ==================== MAIN TTS ====================

export async function speakResponse(
  text: string,
  options?: { onDone?: () => void; onStart?: () => void; emotion?: string }
): Promise<void> {
  try {
    const clean = cleanTextForSpeech(text);
    if (!clean) {
      options?.onDone?.();
      return;
    }

    const store = useTwinStore.getState();
    const twinGender = store.twinGender || 'female';
    const lang = store.lang || 'ar';
    const tier = store.tier || 'free';

    options?.onStart?.();

    // ✅ الباقات المدفوعة: نستخدم الخادم (ElevenLabs/Edge TTS)
    if (tier && ['premium', 'pro', 'yearly'].includes(tier)) {
      try {
        const response = await API.post('/api/voice/speak', {
          text: clean,
          tier,
          gender: twinGender,
          language: lang === 'ar' ? 'ar' : 'en',
          emotion: options?.emotion || 'neutral',
        }, { responseType: 'arraybuffer' });

        if (response.data?.byteLength > 0) {
          const { Audio } = require('expo-av');
          const sound = new Audio.Sound();
          await sound.loadAsync({ uri: `data:audio/mp3;base64,${arrayBufferToBase64(response.data)}` });
          await new Promise<void>((resolve) => {
            sound.setOnPlaybackStatusUpdate((status: any) => {
              if (status.isLoaded && status.didJustFinish) {
                sound.unloadAsync();
                resolve();
              }
            });
            sound.playAsync();
          });
          options?.onDone?.();
          return;
        }
      } catch (e) {
        console.warn("Server voice failed, falling back to local TTS");
      }
    }

    // ✅ الباقات المجانية: Edge TTS عبر الخادم أولاً، ثم Expo Speech
    try {
      const response = await API.post('/api/voice/speak', {
        text: clean,
        tier: 'free',
        gender: twinGender,
        language: lang === 'ar' ? 'ar' : 'en',
        emotion: options?.emotion || 'neutral',
      }, { responseType: 'arraybuffer' });

      if (response.data?.byteLength > 0) {
        const { Audio } = require('expo-av');
        const sound = new Audio.Sound();
        await sound.loadAsync({ uri: `data:audio/mp3;base64,${arrayBufferToBase64(response.data)}` });
        await new Promise<void>((resolve) => {
          sound.setOnPlaybackStatusUpdate((status: any) => {
            if (status.isLoaded && status.didJustFinish) {
              sound.unloadAsync();
              resolve();
            }
          });
          sound.playAsync();
        });
        options?.onDone?.();
        return;
      }
    } catch (e) {
      console.warn("Edge TTS failed, using Expo Speech");
    }

    // ✅ Fallback: Expo Speech محلي مع صوت مناسب للجنس
    const defaultVoice = GENDER_VOICES[twinGender] || GENDER_VOICES.female;
    await Speech.stop();
    Speech.speak(clean, {
      language: lang === 'ar' ? "ar-SA" : "en-US",
      pitch: twinGender === 'female' ? 1.1 : 0.9,
      rate: 0.9,
      voice: defaultVoice,
      onDone: () => options?.onDone?.(),
      onError: () => options?.onDone?.(),
    });
  } catch (e) {
    console.warn("speakResponse error:", e);
    options?.onDone?.();
  }
}

// ==================== STT (Whisper) ====================

export async function transcribeAudio(audioBase64: string): Promise<string> {
  const MAX_RETRIES = 3;
  const TIMEOUT = 30000;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const store = useTwinStore.getState();
      const lang = store.lang === 'ar' ? 'ar' : 'en';

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);

      const response = await API.post('/api/stt', {
        audio: audioBase64,
        language: lang,
      }, { signal: controller.signal });

      clearTimeout(timeoutId);

      if (!response.data?.text) throw new Error('No text returned');
      return response.data.text;
    } catch (e) {
      console.warn(`STT attempt ${attempt} failed:`, e);
      if (attempt === MAX_RETRIES) return '';
      await new Promise(r => setTimeout(r, attempt * 1000));
    }
  }
  return '';
}

// ==================== CONTROLS ====================

export function stopSpeaking(): void {
  Speech.stop();
}

export function isSpeaking(): Promise<boolean> {
  return Speech.isSpeakingAsync();
}
