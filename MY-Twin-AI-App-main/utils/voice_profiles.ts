// ── أنماط الشخصية الصوتية ──────────────────────
export interface VoiceProfile {
  id: string;
  name_ar: string;
  name_en: string;
  pitch: number;
  rate: number;
  language: string;
  emotion_modifier: Record<string, { pitch: number; rate: number }>;
  // ✅ دعم الجنس: لكل جنس إعدادات مختلفة
  gender_overrides?: Record<string, { pitch: number; rate: number }>;
}

export const VOICE_PROFILES: Record<string, VoiceProfile> = {
  wise: {
    id: "wise",
    name_ar: "حكيم",
    name_en: "Wise",
    pitch: 0.9,
    rate: 0.8,
    language: "ar-SA",
    emotion_modifier: {
      joy:     { pitch: 1.0, rate: 0.85 },
      sadness: { pitch: 0.8, rate: 0.7  },
      neutral: { pitch: 0.9, rate: 0.8  },
    },
    gender_overrides: {
      male:   { pitch: 0.85, rate: 0.78 },
      female: { pitch: 0.95, rate: 0.82 },
    },
  },
  fun: {
    id: "fun",
    name_ar: "مرح",
    name_en: "Fun",
    pitch: 1.15,
    rate: 1.0,
    language: "ar-SA",
    emotion_modifier: {
      joy:     { pitch: 1.25, rate: 1.05 },
      sadness: { pitch: 1.0,  rate: 0.9  },
      neutral: { pitch: 1.15, rate: 1.0  },
    },
    gender_overrides: {
      male:   { pitch: 1.05, rate: 0.98 },
      female: { pitch: 1.2,  rate: 1.02 },
    },
  },
  romantic: {
    id: "romantic",
    name_ar: "رومانسي",
    name_en: "Romantic",
    pitch: 1.05,
    rate: 0.8,
    language: "ar-SA",
    emotion_modifier: {
      joy:     { pitch: 1.15, rate: 0.85 },
      sadness: { pitch: 0.9,  rate: 0.7  },
      neutral: { pitch: 1.05, rate: 0.8  },
    },
    gender_overrides: {
      male:   { pitch: 0.95, rate: 0.78 },
      female: { pitch: 1.1,  rate: 0.82 },
    },
  },
  coach: {
    id: "coach",
    name_ar: "مدرب",
    name_en: "Coach",
    pitch: 1.0,
    rate: 0.9,
    language: "ar-SA",
    emotion_modifier: {
      joy:     { pitch: 1.1, rate: 0.95 },
      sadness: { pitch: 0.9, rate: 0.8  },
      neutral: { pitch: 1.0, rate: 0.9  },
    },
    gender_overrides: {
      male:   { pitch: 0.95, rate: 0.88 },
      female: { pitch: 1.05, rate: 0.92 },
    },
  },
  calm: {
    id: "calm",
    name_ar: "هادئ",
    name_en: "Calm",
    pitch: 0.85,
    rate: 0.75,
    language: "ar-SA",
    emotion_modifier: {
      joy:     { pitch: 0.95, rate: 0.8  },
      sadness: { pitch: 0.8,  rate: 0.7  },
      neutral: { pitch: 0.85, rate: 0.75 },
    },
    gender_overrides: {
      male:   { pitch: 0.8,  rate: 0.73 },
      female: { pitch: 0.9,  rate: 0.77 },
    },
  },
};

// ✅ أصوات Edge TTS حسب الجنس واللغة
export const EDGE_VOICE_IDS: Record<string, Record<string, string>> = {
  ar: {
    male:   'ar-EG-ShakirNeural',
    female: 'ar-EG-SalmaNeural',
  },
  en: {
    male:   'en-US-GuyNeural',
    female: 'en-US-JennyNeural',
  },
};

// ✅ الحصول على معرف الصوت المناسب حسب الجنس واللغة
export function getEdgeVoiceId(
  gender: 'male' | 'female' = 'female',
  language: string = 'ar'
): string {
  const langPrefix = language.startsWith('ar') ? 'ar' : 'en';
  return EDGE_VOICE_IDS[langPrefix]?.[gender] || EDGE_VOICE_IDS.ar.female;
}

// ✅ الحصول على إعدادات شخصية صوتية (مع دعم الجنس والعاطفة)
export function getVoiceProfile(
  personality: string,
  emotion?: string,
  gender: 'male' | 'female' = 'female'
): { pitch: number; rate: number; language: string; voiceId: string } {
  const profile = VOICE_PROFILES[personality] || VOICE_PROFILES.calm;
  let pitch = profile.pitch;
  let rate = profile.rate;

  // ✅ تطبيق إعدادات الجنس أولاً
  if (profile.gender_overrides?.[gender]) {
    const override = profile.gender_overrides[gender];
    pitch = override.pitch;
    rate = override.rate;
  }

  // ✅ تطبيق العاطفة فوق إعدادات الجنس
  if (emotion && profile.emotion_modifier[emotion]) {
    const mod = profile.emotion_modifier[emotion];
    pitch = mod.pitch;
    rate = mod.rate;
  }

  const voiceId = getEdgeVoiceId(gender, profile.language);

  return { pitch, rate, language: profile.language, voiceId };
}
