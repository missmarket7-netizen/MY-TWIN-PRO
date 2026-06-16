import * as Speech from "expo-speech";
import { useTwinStore } from "../store/useTwinStore";
import { API } from "../lib/api";

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
    const lang = store.lang || 'ar';

    // نرسل إلى الخادم الذي يختار المزود حسب الباقة
    try {
      const response = await API.post('/api/voice/speak', {
        text: clean,
        gender: twinGender,
        language: lang === 'ar' ? 'ar' : 'en',
        emotion: options?.emotion || 'neutral',
        tier: store.tier || 'free',
      }, { responseType: 'arraybuffer' });

      if (response.data?.byteLength > 0) {
        const { Audio } = require('expo-av');
        const sound = new Audio.Sound();
        await sound.loadAsync({ uri: `data:audio/mp3;base64,${_arrayBufferToBase64(response.data)}` });
        await sound.playAsync();
        return;
      }
    } catch (e) {
      console.warn("Server voice failed, using local fallback");
    }

    // احتياطي: Expo Speech محلي
    await Speech.stop();
    Speech.speak(clean, {
      language: lang === 'ar' ? "ar-SA" : "en-US",
      pitch: options?.pitch || 1.0,
      rate: options?.rate || 0.9,
    });
  } catch (e) {
    console.warn("speakResponse error:", e);
  }
}

function _arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

export async function transcribeAudio(audioBase64: string): Promise<string> {
  try {
    const store = useTwinStore.getState();
    const response = await API.post('/api/stt', {
      audio: audioBase64,
      language: store.lang === 'ar' ? 'ar' : 'en',
    });
    return response.data?.text || '';
  } catch (e) {
    console.warn("STT failed:", e);
    return '';
  }
}

export function stopSpeaking(): void { Speech.stop(); }
export function isSpeaking(): Promise<boolean> { return Speech.isSpeakingAsync(); }
